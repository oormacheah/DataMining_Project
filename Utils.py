import numpy as np
import pandas as pd
import math
import pylev
from scipy import spatial
import re


def get_index_sim(size, first_index, second_index) :
    return int(((2*size - (first_index+1)) * first_index) / 2 + (second_index - first_index) -1)

def get_indices_sim(size, index_new) :
    
    if index_new < size - 1 :
        return (0, index_new + 1)   
    
    else :
        lower_bound = int(size - 1.5 - math.sqrt((size - 1.5)**2 - 2*(index_new - size + 1)))
        upper_bound = int(size - 0.5 - math.sqrt((size - 0.5)**2 - 2*index_new)) + 1
        
        tmp = lower_bound
        continu = True
        while continu :
            if ((2*size - (tmp+1)) * tmp) / 2 <= index_new :
                a = tmp
                tmp += 1
            
            else : 
                continu = False
            
        return (a, int(index_new - (((2*size - (a+1)) * a) / 2) + a + 1))


def rowIndex(row):
    return row.name


def process_frame(frame) :
    frame = frame.lower()
    frame = frame.replace('$','')
    frame = frame.replace('/','')
    frame = frame.replace('<','')
    frame = frame.replace('>','')
    return frame

def get_weight_stack(stack, dict_idf_frames, alpha, beta, gamma) :

    local_weights = [1 / (1 + i) ** alpha for i, _ in enumerate(stack)]
    global_weights = []
    for frame in stack :
        if frame in dict_idf_frames :
            global_weights.append(1 / (1 + math.exp(-beta * (dict_idf_frames[frame] - gamma))))
        else :
            global_weights.append(1 / (1 + math.exp(beta * gamma)))
    return [lw * gw for lw, gw in zip(local_weights, global_weights)]


def levenshtein_dist_weights(frames1, weights1, frames2, weights2) :
    matrix = [[0.0 for _ in range(len(frames1) + 1)] for _ in range(len(frames2) + 1)]

    prev_column = matrix[0]

    for i in range(len(frames1)):
        prev_column[i + 1] = prev_column[i] + weights1[i]

    if len(frames1) == 0 or len(frames2) == 0:
        return 0.0

    curr_column = matrix[1]

    for i2 in range(len(frames2)):

        frame2 = frames2[i2]
        weight2 = weights2[i2]

        curr_column[0] = prev_column[0] + weight2

        for i1 in range(len(frames1)):

            frame1 = frames1[i1]
            weight1 = weights1[i1]

            if frame1 == frame2:
                curr_column[i1 + 1] = prev_column[i1]
            else:
                change = weight1 + weight2 + prev_column[i1]
                remove = weight2 + prev_column[i1 + 1]
                insert = weight1 + curr_column[i1]

                curr_column[i1 + 1] = min(change, remove, insert)

        if i2 != len(frames2) - 1:
            prev_column = curr_column
            curr_column = matrix[i2 + 2]

    return curr_column[-1]  


def split(txt, seps):
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]


def process_stack_trace(stack_trace) :
    
    if len(stack_trace.split('Caused by :')) == 1 : # no Caused by
        listStackTrace = split(stack_trace,('\at ','\tat','\nat',' at '))[1:]
        return (listStackTrace, False, False, [])
    else : # Caused by
        parts = stack_trace.split('Caused by :')
        typeCausedBy = parts[1].split(':')[0].split('class ')[-1]
        listStackTrace = split(parts[0],('\at ','\tat','\nat',' at '))[1:]
        listStackTraceCausedBy = split(parts[1],('at ','\tat'))[1:]
        return (listStackTrace, True, typeCausedBy, listStackTraceCausedBy)

def extract_top_method(list_stack_trace):
    if list_stack_trace : 
        return list_stack_trace[0]
    else :
        return None

def handle_truncated(list_stack_trace):
    if list_stack_trace :
        isMatch = re.search(r"[\(].*?[\)]", list_stack_trace[-1])
        if isMatch :
            return list_stack_trace
        else : 
            return list_stack_trace[:-1]
    else :
        return list_stack_trace

def delete_infoFile(list_stack_trace):
    for i in range(len(list_stack_trace)) :
        list_stack_trace[i] = re.sub(r"[\(].*?[\)]","",list_stack_trace[i])
    
    return list_stack_trace
