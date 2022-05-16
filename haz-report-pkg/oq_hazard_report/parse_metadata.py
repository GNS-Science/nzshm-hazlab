from .base_functions import *

from openquake.baselib.general import BASE183

def check_vs30(data):
    vs30 = np.unique(pd.DataFrame(data['metadata']['sites'])['vs30'])
    
    if len(vs30) == 1:
        vs30 = int(vs30[0])
    else:
        raise NameError('There are multiple vs30 values in the hdf5')
        
    return vs30


def parse_logic_tree_branches(file_id):

    with h5py.File(file_id) as hf:

        # read and prepare the source model logic tree for documentation
        source_lt = pd.DataFrame(hf['full_lt']['source_model_lt'][:])
        for col in source_lt.columns[:-1]:
            source_lt.loc[:,col] = source_lt[col].str.decode('ascii')

        source_lt.loc[:,'branch_code'] = [x for x in BASE183[0:len(source_lt)]]
        source_lt.set_index('branch_code',inplace=True)

        # find the order of the source type tags in the source labels
        source_tags={'C':'Crustal','H':'Hikurangi','P':'Puysegur','f':'Distributed Seismicity'}
        source_types = [source_tags[x[0]] for x in source_lt['branch'][0].split('|')]
        for source_id in source_lt.index:
            for i,source in enumerate(source_lt.loc[source_id,'branch'].split('|')):
                source_lt.loc[source_id,source_types[i]] = source

        # set a standard order for documenting the source types
        source_types = ['Crustal','Hikurangi','Puysegur','Distributed Seismicity']

        # read and prepare the gsim logic tree for documentation
        gsim_lt = pd.DataFrame(hf['full_lt']['gsim_lt'][:])
        for col in gsim_lt.columns[:-1]:
            gsim_lt.loc[:,col] = gsim_lt.loc[:,col].str.decode('ascii')

        gsim_lt_dict = {}
        for i,trt in enumerate(np.unique(gsim_lt['trt'])):
            df = gsim_lt[gsim_lt['trt']==trt]
            df.loc[:,'branch_code'] = [x[1] for x in df['branch']]
            df.set_index('branch_code',inplace=True)
            for j,x in zip(df.index,df['uncertainty']):
                tags = re.split('\[|\]|\nregion = \"|\"',x)
                if len(tags) > 4:
                    df.loc[j,'model name'] = f'{tags[1]}_{tags[3]}'
                else:
                    df.loc[j,'model name'] = tags[1]
            gsim_lt_dict[i] = df

    # read and prep the realization record from documentation
    dstore = datastore.read(file_id)
    rlz_lt = pd.DataFrame(dstore['full_lt'].rlzs).drop('ordinal',axis=1)

    for i_rlz in rlz_lt.index:
        srm_code,gsim_codes = rlz_lt.loc[i_rlz,'branch_path'].split('~')
        rlz_lt.loc[i_rlz,source_types] = source_lt.loc[srm_code,source_types]

        for i,gsim_code in enumerate(gsim_codes):
            trt,gsim = gsim_lt_dict[i].loc[gsim_code,['trt','model name']]
            rlz_lt.loc[i_rlz,trt] = gsim
            
    return source_lt, gsim_lt_dict, rlz_lt


def create_metadata_sheet(f,export_name,vs30,hazard_id,rlz_lt,gsim_lt_dict):
    
    sheet_name ='metadata'
    startrow = 1
    startcol = 2
    
    summary = pd.DataFrame()
    summary.loc['analysis version','col'] = export_name
    summary.loc['vs30','col'] = vs30
    summary.loc['link for plots','col'] = f'http://nzshm22-static-reports.s3-wbsite-ap-southeast-2.amazonaws.com/openquake/DATA/{hazard_id}/hazard_report/index.html'
    summary.to_excel(f,sheet_name=sheet_name,startrow=startrow,startcol=1,header=False)
    startrow += len(summary) + 4
    
    # set a standard order for documenting the source types
    source_types = ['Crustal','Hikurangi','Puysegur','Distributed Seismicity']
    
    variables = ['Deformation model','N','B','Area->Mag Relation','Total Num Earthquakes']

    for source_type in source_types[:-1]:
        summary = pd.DataFrame()

        temp = pd.DataFrame([tag.split('_') for tag in np.unique(rlz_lt[source_type])],columns=variables,index=np.unique(rlz_lt[source_type]))
        temp['Mag Distribution'] = [(temp.loc[i,'N'],temp.loc[i,'B']) for i in temp.index]
        for col in ['N','B','Area->Mag Relation','Total Num Earthquakes']:
            temp[col] = [float(x[1:]) for x in temp[col]]
        record = temp[['Deformation model','Mag Distribution','Total Num Earthquakes','Area->Mag Relation']]

        deformations = np.unique(temp['Deformation model'].values).tolist()
        if source_type == 'Hikurangi':
            deform_labels = ['trench-creeping','trench-locked']
        else:
            deform_labels = ['geological']
        for deform in deformations:
            i = deformations.index(deform)
            temp.loc[temp['Deformation model']==deform,'Deformation model'] = deform_labels[i]
            summary.loc[i,'Deformation model'] = deform_labels[i]

            
        angles = np.unique(temp['Mag Distribution'].values)
        if len(angles) == 1:
            mfd_angle_labels = ['central']
        else:
            mfd_angle_labels = ['more high magnitudes','central','fewer high magnitudes']
        for n_b in angles:
            n = float(n_b[0][1:])
            i = np.searchsorted(np.sort(np.unique(temp['N'].values)), n)
            temp.loc[temp['Mag Distribution']==n_b,'Mag Distribution'] = mfd_angle_labels[i]
            summary.loc[i,'Mag Distribution'] = mfd_angle_labels[i]

            
        amplitudes = np.unique(temp['Total Num Earthquakes'].values)
        if len(amplitudes) == 1:
            mfd_amplitude_labels = ['central'] 
        else:
            mfd_amplitude_labels = ['low','central','high'] 
        for amp in amplitudes:
            i = np.searchsorted(np.sort(amplitudes), amp)
            temp.loc[temp['Total Num Earthquakes']==amp,'Total Num Earthquakes'] = mfd_amplitude_labels[i]
            summary.loc[i,'Total Num_Earthquakes'] = mfd_amplitude_labels[i]

            
        mag_scales = np.unique(temp['Area->Mag Relation'].values)
        if len(mag_scales) == 1:
            mag_scale_labels = ['central']
        elif len(mag_scales) == 2:
            mag_scale_labels = ['central','higher magnitude']
        else:
            mag_scale_labels = ['lower magnitude','central','higher magnitude']
        for mag_scale in mag_scales:
            i = np.searchsorted(np.sort(mag_scales), mag_scale)
            temp.loc[temp['Area->Mag Relation']==mag_scale,'Area->Mag Relation'] = mag_scale_labels[i]
            summary.loc[i,'Area->Mag Relation'] = mag_scale_labels[i]

            
        pd.DataFrame(columns=[source_type]).to_excel(f,sheet_name=sheet_name,startrow=startrow-1,startcol=startcol-1,index=False)
        summary.to_excel(f,sheet_name=sheet_name,startrow=startrow,startcol=startcol,index=False)
        [_,width] = summary.shape
        record.to_excel(f,sheet_name=sheet_name,startrow=startrow,startcol=startcol+5)
        startrow += len(record) + 5
        
    for source_type in source_types[-1:]:
        summary = pd.DataFrame()
        summary.loc[0,'temporal distribution'] = 'no EEPAS clustering'
        summary.loc[0,'uncertainty dispersion'] = 'Poisson'
        pd.DataFrame(columns=[source_type]).to_excel(f,sheet_name=sheet_name,startrow=startrow-1,startcol=startcol-1,index=False)
        summary.to_excel(f,sheet_name=sheet_name,startrow=startrow,startcol=startcol,index=False)
        startrow += len(record) + 5
        

    pd.DataFrame(columns=['Ground motion models']).to_excel(f,sheet_name=sheet_name,startrow=startrow-1,startcol=startcol-1,index=False)
    for i,df in gsim_lt_dict.items():
        trt = np.unique(df['trt'].values)[0]
        gsim_list = pd.concat({trt:df[['weight','model name']]},axis=1)
        gsim_list.to_excel(f,sheet_name=sheet_name,startrow=startrow,startcol=startcol)
        startrow += len(gsim_list) + 5
        
        
    startrow += 5
    rlz_lt.to_excel(f,sheet_name='metadata',startrow=startrow)


def create_metadata_file(export_name,vs30,hazard_id,rlz_lt,gsim_lt_dict):

    filename = f'{export_name}_metadata_vs30-{vs30}.xlsx'
    with pd.ExcelWriter(filename) as f:
        create_metadata_sheet(f,export_name,vs30,hazard_id,rlz_lt,gsim_lt_dict)
        
    # read data and recreate sheet with autoset columns widths
    metadata = pd.read_excel(filename,sheet_name='metadata')
    
    with pd.ExcelWriter(filename) as f:
        # recreating the metadata sheet will keep the bold formatting
        create_metadata_sheet(f,export_name,vs30,hazard_id,rlz_lt,gsim_lt_dict)
        _ = [f.sheets['metadata'].set_column(i,i,max([len(str(s)) for s in metadata[col].values]+[len(col)])+2) for i,col in enumerate(metadata.columns)]


def create_hcurves_single_vs30(export_name,vs30,hazard_id,parameters_for_exporting,data):
    
    sites_for_exporting = parameters_for_exporting['sites']
    imts_for_exporting = parameters_for_exporting['imts']
    
    metadata_file = f'{export_name}_metadata_vs30-{vs30}.xlsx'
    metadata = pd.read_excel(metadata_file,sheet_name='metadata')
    
    filename = f'{export_name}_hcurves_vs30-{vs30}.xlsx'
    with pd.ExcelWriter(filename) as f:

        # recreating the metadata sheet will keep the bold formatting
        create_metadata_sheet(f,export_name,vs30,hazard_id,rlz_lt,gsim_lt_dict)
        _ = [f.sheets['metadata'].set_column(i,i,max([len(str(s)) for s in metadata[col].values]+[len(col)])+2) for i,col in enumerate(metadata.columns)]

        intensity_type = 'acc'
        sites = pd.DataFrame(data['metadata']['sites'])
        imtls = data['metadata'][f'{intensity_type}_imtls']
        quantiles = data['metadata']['quantiles']
        n_stats = len(quantiles)+1
        hcurves_rlzs = np.array(data['hcurves']['hcurves_rlzs'])
        hcurves_stats = np.array(data['hcurves']['hcurves_stats'])

        for site in sites_for_exporting:
            for imt in imts_for_exporting:

                site_idx = sites.loc[site,'sids']
                imt_idx = list(imtls.keys()).index(imt)

                stats = pd.DataFrame(np.transpose(hcurves_stats[site_idx,imt_idx,:,:]),columns=imtls[imt])
                stats[''] = ['mean'] + quantiles
                stats.set_index('',inplace=True)

                stats.to_excel(f,sheet_name=f'{site}_{imt}')
                pd.DataFrame(np.transpose(hcurves_rlzs[site_idx,imt_idx,:,:]),columns=imtls[imt]).to_excel(f,sheet_name=f'{site}_{imt}',startrow=n_stats+2,header=False)


def create_uhs_single_vs30(export_name,vs30,parameters_for_exporting,data):
    
    sites_for_exporting = parameters_for_exporting['sites']
    rps_for_exporting = parameters_for_exporting['rps']
    
    metadata_file = f'{export_name}_metadata_vs30-{vs30}.xlsx'
    metadata = pd.read_excel(metadata_file,sheet_name='metadata')

    filename = f'{export_name}_uhs_vs30-{vs30}.xlsx'
    with pd.ExcelWriter(filename) as f:

        # recreating the metadata sheet will keep the bold formatting
        create_metadata_sheet(f,export_name,vs30,hazard_id,rlz_lt,gsim_lt_dict)
        _ = [f.sheets['metadata'].set_column(i,i,max([len(str(s)) for s in metadata[col].values]+[len(col)])+2) for i,col in enumerate(metadata.columns)]

        intensity_type = 'acc'
        sites = pd.DataFrame(data['metadata']['sites'])
        imtls = data['metadata'][f'{intensity_type}_imtls']
        periods = [period_from_imt(imt) for imt in list(imtls.keys())]
        quantiles = data['metadata']['quantiles']
        n_stats = len(quantiles)+1
            
        for i,intensity_type in enumerate(['acc','disp']):

            startcol = [0,len(periods)+2][i]
            if intensity_type == 'acc':
                label = 'Pseudo Spectral Accelerations, Sa(T) [g]'
            elif intensity_type == 'disp':
                label = 'Pseudo Spectral Displacements, Sd(T) [m]'
                
            hazard_rps = data['hazard_design']['hazard_rps']
            hazard_rlzs = np.array(data['hazard_design'][intensity_type]['im_hazard'])
            hazard_stats = np.array(data['hazard_design'][intensity_type]['stats_im_hazard'])

            for site in sites_for_exporting:
                for rp in rps_for_exporting:

                    site_idx = sites.loc[site,'sids']
                    rp_idx = hazard_rps.index(rp)

                    stats = pd.DataFrame(np.transpose(hazard_stats[site_idx,:,rp_idx,:]),columns=periods)
                    stats[''] = ['mean'] + quantiles
                    stats.set_index('',inplace=True)
                    stats = pd.concat({label:stats},axis=1)

                    stats.to_excel(f,sheet_name=f'{site}_1in{rp}',startcol=startcol)
                    pd.DataFrame(np.transpose(hazard_rlzs[site_idx,:,rp_idx,:,0]),columns=periods).to_excel(f,sheet_name=f'{site}_1in{rp}',startrow=n_stats+5,startcol=startcol,header=False)

