#!/usr/bin/env python
# -*- coding: utf-8 -*-

import eel
from classes import Population, Individual
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import glob
import moviepy.editor as mpy
from pathlib import Path
from weasyprint import HTML
import os
from jinja2 import Environment, FileSystemLoader
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
import pdfkit
import csv
from datetime import date
import pendulum
from tkinter import Tk
from tkinter.filedialog import askopenfilename


eel.init('web')


@eel.expose
def item_creator(values, dates, name):
    dist = []
    focusPoint = []
    for d in range (0, len(values)):
        currentDate = []
        currentDate = dates[d].split("/")
        print(currentDate[0])
        print(currentDate[1])
        print(currentDate[2])
        print(currentDate)
        focusPoint.append(pendulum.datetime(int(currentDate[0]), 
                                            int(currentDate[1]), 
                                            int(currentDate[2])))
    span = float((focusPoint[-1] - focusPoint[0]).in_days())
    for date in range (0, len(focusPoint)):
        if (date == 0):
            dist.append(-2.0)
        else:
            slot = float((focusPoint[date] - focusPoint[date - 1]).in_days())
            dist.append((4 * slot / span) + float(dist[date - 1]))
    file = 'data/custom/' + name + '.csv'
    with open(file, mode='a', newline='') as results_f:
        results_w = csv.writer(results_f, delimiter=',')
        results_w.writerow(['X','step', name])
        for point in range (0, len(values)):
            results_w.writerow([dist[point],1,values[point]])


@eel.expose
def remove_gif():
    if Path('web/img/ultimateBar.png').is_file():
        os.remove('web/img/scatter.gif')
        os.remove('web/img/bar.gif')
        os.remove('web/img/ultimate.png')
        os.remove('web/img/ultimateBar.png')
        os.remove('web/report.pdf')


@eel.expose
def check_gif(path):
    gif = Path(path + "/scatter.gif")
    if gif.is_file():
        return True
    else:
        return False


def create_gif(name):
    gif_name = 'web/img/' + name
    fps = 24
    file_list = glob.glob('*' + name + '.png')
    list.sort(file_list, key=lambda x: int(x.split(name + '.png')[0]))
    clip = mpy.ImageSequenceClip(file_list, fps=fps)
    clip.write_gif('{}.gif'.format(gif_name), fps=fps)


def generate_report(markers, yresult, path):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template("web/results.html")
    template_vars = {"first_projection": yresult[0],
                     "second_projection": yresult[1],
                     "third_projection": yresult[2],
                     "fourth_projection": yresult[3],
                     "first_marker": markers[0],
                     "second_marker": markers[1],
                     "third_marker": markers[2],
                     "last_marker": markers[3]}
    html_out = template.render(template_vars)
    HTML(string=html_out).write_pdf("web/report_pt2.pdf")
    pdfkit.from_file('web/graphs.html', 'web/report_pt1.pdf')
    merge_pdf()


def merge_pdf():
    file1 = PdfFileReader(open('web/report_pt1.pdf', "rb"))
    file2 = PdfFileReader(open('web/report_pt2.pdf', "rb"))
    output = PdfFileWriter()
    page = file1.getPage(0)
    page.mergePage(file2.getPage(0))
    output.addPage(page)
    outputStream = open('web/report.pdf', "wb")
    output.write(outputStream)
    outputStream.close()


@eel.expose
def open_report(path):
    os.startfile(path + '/web/report.pdf')


@eel.expose
def open_results(path):
    os.startfile(path)


@eel.expose
def check_report(path):
    repo = Path(path + '/report.pdf')
    if repo.is_file():
        return True
    else:
        return False


def create_csv(timeframe, results, markers):
    file = 'data/res/' + timeframe + '_proj_' + str(date.today()) + '.csv'
    with open(file, mode='a', newline='') as results_f:
        results_w = csv.writer(results_f, delimiter=',')
        if (os.stat(file).st_size == 0):
            results_w.writerow([markers[0], markers[1], markers[2], markers[3]])
        results_w.writerow([results[0], results[1], results[2], results[3]])


@eel.expose
def carnitas(gen, minGen, limit, choice, degree, acpErr):
    plt.style.use('seaborn')
    if int(choice) == 0:
        df = pd.read_csv('data/anual.csv')
        function = 'anual'
    elif int(choice) == 1:
        df = pd.read_csv('data/semanal.csv')
        function = 'semanal'
    else:
        Tk().withdraw()
        selectedFile = askopenfilename()
        df = pd.read_csv(selectedFile)
        function = selectedFile[43:].replace('.csv', '')
    lookupTable = {}
    for i, record in df.iterrows():
        key = record['X']
        lookupTable[key] = record[function]
    generations = int(gen)
    degrees = int(degree)
    min_generations = int(minGen)
    min_error = int(acpErr)
    limit = int(limit)
    PATH = "C:/Users/Paredon/Desktop/tesis"  # Pendiente con esto
    polynomials = Population(degrees, 1)
    polynomials.evaluate(lookupTable)
    polynomials.sort()
    for g in range(generations):
        if (g > limit):
            if ((g > min_generations and polynomials.best[-1].fitness ==
                    polynomials.best[-limit].fitness) or
                    polynomials.best[-1].fitness < min_error):
                break
        polynomials.enhance(lookupTable)
        polynomials.plot2D(df['X'], df[function], g, PATH, generations)
        polynomials.plotBar(df['X'], df[function], g, PATH, generations)
    create_gif("scatter")
    create_gif("bar")
    for g in range(generations):
        if Path(str(g) + 'scatter.png').is_file():
            os.remove(str(g) + 'scatter.png')
            os.remove(str(g) + 'bar.png')
    polynomials.best[-1].roundCoefficients()
    poly = polynomials.best[-1].display()
    p = np.poly1d(poly)
    preres = []
    yresult = []
    if int(choice) == 0:
        xpred = [0.2, 0.6, 1.2, 2.4]
        markers = ['1 mes: ', '3 meses: ', '6 meses: ', '1 año: '] 
        for r in xpred:
            preres.append(round(p(r), 5))
        yresult = [x * 10000 for x in preres]
        create_csv('Yearly', yresult, markers)
    else:
        markers = ['1 día: ', '3 días: ', '6 días: ', '1 semana: ']
        xpred = [2.029, 2.086, 2.143, 2.2]
        for r in xpred:
            preres.append(round(p(r), 4))
        yresult = [x * 100 for x in preres]
        create_csv('Weekly', yresult, markers)
    generate_report(markers, yresult, PATH)
    return yresult


eel.start('main.html', size=(1310, 800))
