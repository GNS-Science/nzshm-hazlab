from dataclasses import dataclass
from pathlib import PurePath, Path
from unittest import result
import matplotlib.pyplot as plt
import markdown
from markdown.extensions.toc import TocExtension
import os

from zipfile import ZipFile

import oq_hazard_report.read_oq_hdf5
import oq_hazard_report.plotting_functions

from oq_hazard_report.resources.css_template import css_file

HEAD_HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>##TITLE##</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="hazard_report.css">
<style>
    .markdown-body {
        box-sizing: border-box;
        min-width: 200px;
        max-width: 1000px;
        margin: 0 auto;
        padding: 45px;
    }

    @media (max-width: 767px) {
        .markdown-body {
            padding: 15px;
        }
    }
</style>
</head>
<article class="markdown-body">

'''

TAIL_HTML = '''
</article>
</html>

'''

MAX_ROW_WIDTH = 3


class ReportBuilder:

    #TODO in addition to a zip archive accept a directory or hdf5 
    #TODO currently assume only 1 hdf5 file in the zip, what happens if there are multiple?

    def __init__(self,name='', hazard_archive=None, output_path=None):
        self._name = name
        self._hazard_archive = hazard_archive
        self._output_path = output_path

    def setName(self,name):
        self._name = name
    
    def setHazardArchive(self,archive):
        self._hazard_archive = archive

    def setOutputPath(self,output_path):
        self._output_path = output_path

    def run(self):

        self._plot_dir = Path(self._output_path,'figures')
        if not self._plot_dir.is_dir():
            self._plot_dir.mkdir()


        if not(self._output_path):
            raise Exception("output path must be specified")
        print('extracting archive . . .')
        
        with ZipFile(self._hazard_archive,'r') as zip:
            for n in zip.namelist():
                if 'calc' in n:
                    hdf_file = zip.extract(n,path=self._output_path)
        
        print('done extracting archive')

        plots = self.generate_plots(hdf_file)
        self.generate_report(plots)

        os.remove(hdf_file)

    
    def generate_plots(self,hdf_file):

        def make_hazard_plots(args):
            # loop over sites and imts
            print('generating plots . . .')
            for site in data['metadata']['sites']['custom_site_id'].keys():

                plots.append( dict(
                        level=2,
                        text=site,
                        figs=[])
                    )

                print('site:',site)

                for imt in data['metadata']['acc_imtls'].keys():

                    print('imt:',imt)

                    plot_path = PurePath(self._plot_dir,f'hcurve_{site}_{imt}.png')
                    plot_rel_path = PurePath(plot_path.parent.name,plot_path.name)
                    print('writing',plot_rel_path)

                    fig, ax = plt.subplots(1,1)
                    
                    oq_hazard_report.plotting_functions.plot_hazard_curve(ax=ax, site_list=[site,], imt=imt, **args)
                    plt.savefig(str(plot_path), bbox_inches="tight")

                    plots.append( dict(
                                level=3,
                                text=imt,
                                fig=PurePath(plot_rel_path))
                    )
                    plt.close(fig)

        def make_spectra_plots(rps,args):
            # loop over sites and imts
            print('generating plots . . .')
            for site in data['metadata']['sites']['custom_site_id'].keys():

                plots.append( dict(
                        level=2,
                        text=site,
                        figs=[])
                    )

                print('site:',site)

                for rp in rps:

                    plot_path = PurePath(self._plot_dir,f'spectra_{site}_{rp}.png')
                    plot_rel_path = PurePath(plot_path.parent.name,plot_path.name)
                    print('writing',plot_rel_path)

                    fig, ax = plt.subplots(1,1)
                    
                    oq_hazard_report.plotting_functions.plot_spectrum(ax=ax, rp=rp, site=site, **args)
                    plt.savefig(str(plot_path), bbox_inches="tight")

                    plots.append( dict(
                                level=3,
                                text=rp,
                                fig=PurePath(plot_rel_path))
                    )

                    plt.close(fig)


        data = oq_hazard_report.read_oq_hdf5.retrieve_data(hdf_file)


        plots = []
        # ============ Hazard Curves ============ #
        ref_rps = [50,500] # where it will plot PoE lines #TODO what should this be?
        xlim = [0,5]
        ylim = [1e-6,1]

        args = dict(
            ref_rps=ref_rps,
            xlim=xlim,
            ylim=ylim,
            results=data
        )

        plots.append( dict(
                level=1,
                text='Hazard Curve',
                figs=[])
            )

        print('hazard curves . . .')
        make_hazard_plots(args)
        print('done with hazard curves')

        # # ============ Spectra ============ #
        # args = dict(
        #     color = 'b',
        #     results = data
        # )

        # plots.append( dict(
        #         level=1,
        #         text='Spectra',
        #         figs=[])
        #     )

        # rp = [50,500]

        # print('spectra . . . ')
        # make_spectra_plots(rp, args)
        # print('done with spectra')


        return plots


   

    def generate_plots_dummy(self):

        plots = {}

        figures_dir = PurePath('/home/chrisdc/NSHM/DEV/nzshm_hazlab/examples/Figures_chris')

        types = ['hcurves','disaggs']
        sites = ['Wellington', 'Auckland']
        periods = ['PGA', 'SA(0.5)', 'SA(1.5)', 'SA(3.0)', 'SA(5.0)']

        plots = []

        for t in types:
            plots.append( dict(
                level=1,
                text=t,
                figs=[])
            )
            for site in sites:
                plots.append( dict(
                    level=2,
                    text=site,
                    figs=[])
                )
                for period in periods:
                    if t == 'disaggs':
                        figs = [[PurePath(figures_dir,f'{t}_{site}_{period}_0.002105.png'),
                                PurePath(figures_dir,f'{t}_{site}_{period}_0.000404.png')]]
                        titles = ['10% in 50 years', '2% in 50 years']
                        plots.append( dict(
                            level=3,
                            text=period,
                            fig_table = {'figs':figs, 'titles':titles})
                        )
                    else:
                        plots.append( dict(
                            level=3,
                            text=period,
                            fig=PurePath(figures_dir,f'{t}_{site}_{period}.png'))
                        )
        
        return plots

    def generate_report(self,plots):

        print('generating report . . .')

        md_string = f'# {self._name}\n'
        md_string += '<a name="top"></a>\n'
        md_string += '\n'
        md_string += '[TOC]\n'
        md_string += '\n'

        for plot in plots:
            md_string += f'{"#"*(plot["level"]+1)} {plot["text"]}\n'
            if plot['level'] < 3:
                md_string += f'[top](#top)\n'
            if plot.get('fig'):
                md_string += f'![an image]({plot["fig"]})\n'
            if plot.get('fig_table'):
                md_string += self.build_fig_table(plot.get('fig_table'))

    
        html = markdown.markdown(md_string, extensions=[TocExtension(toc_depth="2-6"),'tables'])

        head_html = HEAD_HTML.replace('##TITLE##',self._name)
        html = head_html + html + TAIL_HTML        
        
        with open(PurePath(self._output_path, 'index.html'),'w') as output_file:
            output_file.write(html)

        with open(PurePath(self._output_path, 'hazard_report.css'),'w') as output_file:
            output_file.write(css_file)

        print('done generating report')


    def build_fig_table(self,fig_table):

        def end_row(table_md):
            return table_md[:-3] + '\n'

        figs = fig_table.get('figs')
        titles = fig_table.get('titles')

        nrows = len(figs)
        ncols = len(figs[0])   

        table_md = ''
        for title in titles:
            table_md += f'{title} | '
        table_md = end_row(table_md)

        for col in range(ncols):
            table_md += '------------- | '
        table_md = end_row(table_md)

        for row in range(nrows):
            for col in range(ncols):
                table_md += f'![an image]({figs[row][col]}) | '
            table_md = end_row(table_md)

        table_md += '\n'
        return table_md



if __name__ == "__main__":

    datadir = '/home/chrisdc/NSHM/DEV/nzshm_hazlab/examples/openquake_hdf5_archive-T3BlbnF1YWtlSGF6YXJkVGFzazoxMDIwMjA='

    report_builder = oq_hazard_report.report_builder.ReportBuilder(output_path="/tmp/hazard_reports")
    report_builder.setName('TEST')
    report_builder.setHazardArchive('/home/chrisdc/NSHM/DEV/nzshm_hazlab/examples/openquake_hdf5_archive-T3BlbnF1YWtlSGF6YXJkVGFzazoxMDIwMjA=.zip')

    

    