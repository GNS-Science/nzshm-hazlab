from pathlib import PurePath
import markdown
from markdown.extensions.toc import TocExtension

from oq_hazard_report.resources.css_template_b import css_file

HEAD_HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Paleo vs No Paleo</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="hazard_report.css">
<style>
    .markdown-body {
        box-sizing: border-box;
        min-width: 200px;
        max-width: 1500px;
        margin: 0 auto;
        padding: 0px;
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

fig_url = 'http://nzshm22-static-reports.s3-website-ap-southeast-2.amazonaws.com/opensha/DATA/###ID###/solution_report/resources/###FIGURE###'

output_path = PurePath('/home/chrisdc/NSHM/inversions')

id_pairs = [
    {'title':'Geologic b=0.823','paleoID':'SW52ZXJzaW9uU29sdXRpb246MTEzMDUz','NOpaleoID':'SW52ZXJzaW9uU29sdXRpb246MTE3MDg5'},
    {'title':'Geologic b=0.959','paleoID':'SW52ZXJzaW9uU29sdXRpb246MTEzMDMy','NOpaleoID':'SW52ZXJzaW9uU29sdXRpb246MTE3MDgw'},
    {'title':'Geologic b=1.089','paleoID':'SW52ZXJzaW9uU29sdXRpb246MTEzMDM5','NOpaleoID':'SW52ZXJzaW9uU29sdXRpb246MTE3MTAx'},

    {'title':'Geodetic b=0.823','paleoID':'SW52ZXJzaW9uU29sdXRpb246MTEzMDY3','NOpaleoID':'SW52ZXJzaW9uU29sdXRpb246MTE4MjUz'},
    {'title':'Geodetic b=0.959','paleoID':'SW52ZXJzaW9uU29sdXRpb246MTEzMDgw','NOpaleoID':'SW52ZXJzaW9uU29sdXRpb246MTE4MjU0'},
    {'title':'Geodetic b=1.089','paleoID':'SW52ZXJzaW9uU29sdXRpb246MTEzMDYz','NOpaleoID':'SW52ZXJzaW9uU29sdXRpb246MTE4MjU5'},
        ]

figures = [
    'misift_progress_STD_DEV.png',
    'mfd_plot_NZ_RECTANGLE_Gridded_Region.png',
    'slip_rates_target.png',
    'slip_rates_sol_scatter.png',
    'slip_rates_log_sol_scatter.png',
    'slip_rates_rel_std_dev.png',
    'slip_rates_std_dev_misfit.png',
    'paleo_rate_scatter.png',
    ]

md_string = '#Inversion Compare\n'
md_string += '<a name="top"></a>\n'
md_string += '\n'
md_string += '[TOC]\n'
md_string += '\n'

for id_pair in id_pairs:
    md_string += f'[top](#top)\n'
    md_string += f'##{id_pair["title"]}\n'
    md_string += '| <span style="font-size:24px">**Paleo Constraint**</span> | <span style="font-size:24px">**NO Paleo Constraint**</span> |\n'
    md_string += '| ---------------- | ------------------- |\n'
    for fig in figures:
        md_string += '| '
        fig1 = fig_url.replace('###ID###',id_pair['paleoID']).replace('###FIGURE###',fig)
        fig2 = fig_url.replace('###ID###',id_pair['NOpaleoID']).replace('###FIGURE###',fig)
        md_string += f'<a href={fig1} target="_blank">![an image]({fig1})</a> | '
        md_string += f'<a href={fig2} target="_blank">![an image]({fig2})</a> |'
        md_string += '\n'
    md_string += '\n'

html = markdown.markdown(md_string, extensions=[TocExtension(toc_depth="2-4"),'tables'])
html = HEAD_HTML + html + TAIL_HTML

with open(PurePath(output_path, 'index.html'),'w') as output_file:
            output_file.write(html)

with open(PurePath(output_path, 'hazard_report.css'),'w') as output_file:
            output_file.write(css_file)

