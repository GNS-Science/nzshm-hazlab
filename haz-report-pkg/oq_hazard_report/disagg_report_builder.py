import numpy as np
from pathlib import Path, PurePath

import markdown
from markdown.extensions.toc import TocExtension

import matplotlib.pyplot as plt

import oq_hazard_report.disagg_plotting_functions as dpf
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


class DisaggReportBuilder:

    def __init__(self,name, disagg_data_filepath, output_path):

        self._name = name
        self._data_filepath = Path(disagg_data_filepath)
        self._output_path = Path(output_path)

        assert self._data_filepath.exists()

        if self._output_path.exists() and (not self._output_path.is_dir()):
            raise Exception(f'output path {self._output_path} is not a directory')
        
        if not self._output_path.exists():
            self._output_path.mkdir()

        

    def load_data(self):
        self._disagg = np.load(self._data_filepath)

    
    def run(self):

        self._plot_dir = Path(self._output_path,'figures')
        if not self._plot_dir.is_dir():
            self._plot_dir.mkdir()

        self.load_data()
        
        plots = self.generate_plots()

        self.generate_report(plots)


    def generate_plots(self):

        plots = []

        plots.append( dict(
                    level=1,
                    text='Tectonic Region Type',
                    figs=[])
                )
        plots += self.make_trt_plot()

        plots.append( dict(
                    level=1,
                    text='Magnitude-Distance',
                    figs=[])
                )
        plots += self.make_mag_dist_plot()


        return plots


    def make_trt_plot(self):
        
        fig, ax = plt.subplots(1,1)
        fig.set_size_inches(7,5)    
        fig.set_facecolor('white')
        plot_path = PurePath(self._plot_dir,'trt_bar.png')
        plot_rel_path = PurePath(plot_path.parent.name,plot_path.name)

        dpf.plot_trt(fig, ax, self._disagg)
        plt.savefig(str(plot_path), bbox_inches="tight")
        plt.close(fig)

        plots = [
            dict(
            level=4,
            text='',
            fig = plot_rel_path
            )
        ]

        return plots


    def make_mag_dist_plot(self):
        
        fig, ax = plt.subplots(1,1)
        fig.set_size_inches(10,6)    
        fig.set_facecolor('white')
        plot_path = PurePath(self._plot_dir,'mag_dist_2d.png')
        plot_rel_path = PurePath(plot_path.parent.name,plot_path.name)

        dpf.plot_mag_dist_2d(fig, ax, self._disagg)
        plt.savefig(str(plot_path), bbox_inches="tight")
        plt.close(fig)

        plots = [
            dict(
            level=4,
            text='',
            fig = plot_rel_path
            )
        ]

        return plots



    def generate_report(self,plots):

        print('generating report . . .')

        md_string = f'# {self._name}\n'
        # md_string += '<a name="top"></a>\n'
        md_string += '\n'
        # md_string += '[TOC]\n'
        md_string += '\n'

        for plot in plots:
            md_string += f'{"#"*(plot["level"]+1)} {plot["text"]}\n'
            # if plot['level'] < 4:
            #     md_string += f'[top](#top)\n'
            if plot.get('fig'):
                md_string += f'<a href={plot["fig"]} target="_blank">![an image]({plot["fig"]})</a>\n'
            if plot.get('fig_table'):
                md_string += self.build_fig_table(plot.get('fig_table'))

    
        # html = markdown.markdown(md_string, extensions=[TocExtension(toc_depth="2-4"),'tables'])
        html = markdown.markdown(md_string,extensions=['tables'])

        head_html = HEAD_HTML.replace('##TITLE##',self._name)
        html = head_html + html + TAIL_HTML        
        
        with open(PurePath(self._output_path, 'index.html'),'w') as output_file:
            output_file.write(html)

        with open(PurePath(self._output_path, 'hazard_report.css'),'w') as output_file:
            output_file.write(css_file)

        print('done generating report')


    def build_fig_table(self,fig_table):

        #TODO error handling for titles and figs not same shape

        def end_row(table_md):
            return table_md[:-3] + '\n'
        
        def insert_header_break(table_md,ncols):
            for col in range(ncols):
                table_md += ': ------------- : | '
            return table_md

        figs = fig_table.get('figs')
        titles = fig_table.get('titles')

        nrows = len(figs)
        ncols = len(figs[0])
        ncols_header = ncols

        table_md = '\n'

        for row in range(nrows):
            ncols = len(figs[row])

            for col in range(ncols):
                table_md += f'{titles[row][col]} | '
                if ncols < ncols_header:
                    for i in range(ncols_header-ncols):
                        table_md += '. | '
            table_md = end_row(table_md)

            if row==0:
                table_md = insert_header_break(table_md,ncols)
                table_md = end_row(table_md)

            for col in range(ncols):
                fig = figs[row][col]
                table_md += f'<a href={fig} target="_blank">![an image]({fig})<a href={fig} target="_blank"> | '
                if ncols < ncols_header:
                    for i in range(ncols_header-ncols):
                        table_md += '. | '

            table_md = end_row(table_md)

        table_md += '\n'

        return table_md        
