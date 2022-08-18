import oq_hazard_report.report_builder
import time


plot_types = ['uhs']
# plot_types = ['hcurve']

#full run
# achive_path = '/home/chrisdc/NSHM/DEV/nzshm_hazlab/data/openquake_hdf5_archive-T3BlbnF1YWtlSGF6YXJkVGFzazoxMDIwMjA=.zip'

# test run
archive_path = '/home/chrisdc/NSHM/DEV/nzshm_hazlab/data/openquake_hdf5_archive-T3BlbnF1YWtlSGF6YXJkVGFzazoxMDEyNjE=.zip'
# TOSHI_ID = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAxMjYy'
TOSHI_ID = 'T3BlbnF1YWtlSGF6YXJkU29sdXRpb246MTAyOTM3'


report_builder_store = oq_hazard_report.report_builder.ReportBuilder(output_path="/tmp/hazard_reports/store")
report_builder_store.setName('store')
report_builder_store.setPlotTypes(plot_types)
report_builder_store.setHazardStore(TOSHI_ID)
t0 = time.perf_counter()
report_builder_store.load_data()
t1 = time.perf_counter()
print('time to load store:',t1-t0)
report_builder_store.run()

# report_builder_hdf = oq_hazard_report.report_builder.ReportBuilder(output_path="/tmp/hazard_reports/hdf")
# report_builder_hdf.setName('HDF5')
# report_builder_hdf.setPlotTypes(plot_types)
# report_builder_hdf.setHazardArchive(archive_path)
# t0 = time.perf_counter()
# report_builder_hdf.load_data()
# t1 = time.perf_counter()
# print('time to load hdf:',t1-t0)
# report_builder_hdf.run()



# data_hdf = report_builder_hdf.data
data_store = report_builder_store.data



