from django.shortcuts import render, render_to_response
#from .forms import MainForm
from django.conf import settings
import os
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support,classification_report
import re
import numpy as np

# Create your views here.
    
def MainView(request):
    return render(request, 'leaseapp/main.html', {})

def RunApp(request):
    results = {}
    # reading static files which are 10 txts files of leases and 
    # nonleases each
    leasedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/leasedata/leases')
    nonleasedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/leasedata/nonleases')
    leasepaths = [os.path.join(leasedir, f) for f in os.listdir(leasedir)]
    nonleasepaths = [os.path.join(nonleasedir, f) for f in os.listdir(nonleasedir)]
    
    def get_f_contents(filepath):
        with open(filepath, 'rb') as f:
            return f.read().decode('utf8', errors='ignore')
    
    lease_contents = [get_f_contents(path) for path in leasepaths]
    nonlease_contents = [get_f_contents(path) for path in nonleasepaths]
    
    LEASE_LABEL = 1
    NONLEASE_LABEL = -1
    # run and get scores    
    def predict_docs(docs, rubric, lease_threshold):
        phrases = rubric.keys()
        pred = []
        for i, doc in enumerate(docs):
            doc_score = 0
            for phrase in phrases:
                # need to use re search to enforce word boundaries
                # else 'in' will match 'ad' in 'read'
                if re.search(r'\b{}\b'.format(phrase), doc, re.I):
                    doc_score = doc_score + rubric[phrase]
            if doc_score > lease_threshold:
                print('Doc {} was predicted as a lease, given a score of {}.'.format(i, doc_score))
                pred.append(LEASE_LABEL)
            else:
                print('Doc {} was not predicted as a lease, given a score of {}.'.format(i, doc_score))
                pred.append(NONLEASE_LABEL)
            #end for
        #end def
        return pred
    
    form_inputs = request.POST
    lease_threshold = float(form_inputs['lease_threshold'])
    phrases = [form_inputs[x] for x in form_inputs.keys() if x.startswith('word') and form_inputs[x]]
    scores = [float(form_inputs[x]) for x in form_inputs.keys() if x.startswith('point') and form_inputs[x]]
    rubric = dict(zip(phrases, scores))
    
    print('predicting leases')
    lease_pred = predict_docs(lease_contents, rubric, lease_threshold)
    print('predicting nonleases')
    nonlease_pred = predict_docs(nonlease_contents, rubric, lease_threshold)
    
    lease_ans = [LEASE_LABEL] * len(lease_contents)
    nonlease_ans = [NONLEASE_LABEL] * len(nonlease_contents) 
    all_predict = lease_pred + nonlease_pred
    all_answers = lease_ans + nonlease_ans
    
    # prepare prf for results
    print(classification_report(all_answers,all_predict))

    metrics_by_class = precision_recall_fscore_support(all_answers, all_predict)
    results['nonlease_prf'] = [metrics_by_class[i][0] for i in range(0,3)]
    results['lease_prf'] = [metrics_by_class[i][1] for i in range(0,3)]
    results['all_prf'] = precision_recall_fscore_support(all_answers, all_predict, average='weighted')
       
    matrix = confusion_matrix(all_answers,all_predict)
    results['TP'] = matrix[0][0]
    results['FN'] = matrix[0][1]
    results['FP'] = matrix[1][0]
    results['TN'] = matrix[1][1]
    print(results)
    return results

def ResultsView(request):
    results = RunApp(request)
    print(results)
    return render_to_response('leaseapp/results.html', context=results)