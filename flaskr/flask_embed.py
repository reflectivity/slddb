from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Legend, LegendItem, HoverTool, WheelZoomTool, TapTool, Tap
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme

from tornado.ioloop import IOLoop
from bokeh.embed import server_document

data={
    'x': [1,2,3],
    'y1': [1,2,3],
    'y2': [1,2,3],
    }

def modify_doc(doc):
    source = ColumnDataSource(data=data)

    ht=HoverTool(
        tooltips=[
            ('E', '@x keV'),
            ('real', '@y1'),  # use @{ } for field names with spaces
            ('imag', '@y2'),
            ],

        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
        )

    plot = figure(title="Energy dependent x-ray SLD", tools='pan,xwheel_zoom,box_zoom,reset,save,tap')
    plot.add_tools(ht)
    plot.toolbar.active_scroll=plot.select_one(WheelZoomTool)

    l1=plot.line('x', 'y1', source=source, line_color='blue')
    l2=plot.line('x', 'y2', source=source, line_color='red')
    legend=Legend(items=[LegendItem(label='real', renderers=[l1], index=0),
                         LegendItem(label='imag', renderers=[l2], index=1),],
                  location='bottom_right')
    plot.add_layout(legend)
    plot.xaxis.axis_label='Energy (keV)'
    plot.yaxis.axis_label='SLD (Å⁻²)'

    doc.add_root(column(plot))

    doc.theme = Theme(filename="flaskr/templates/theme.yaml")


def bk_worker():
    server = Server({'/bkapp': modify_doc}, io_loop=IOLoop(), allow_websocket_origin=["127.0.0.1:80",
                                                                                      "127.0.0.1:8000",
                                                                                      "127.0.0.1:5000"])
    server.start()
    server.io_loop.start()

from threading import Thread
Thread(target=bk_worker, daemon=True).start()

def get_script(x,y1, y2):
    global data
    data['x']=x
    data['y1']=y1
    data['y2']=y2
    return server_document('http://localhost:5006/bkapp')
