#
# Collective Knowledge (Predictive modeling using python sklearn)
#
# See CK LICENSE.txt for licensing details
# See CK Copyright.txt for copyright details
#
# Developer: Grigori Fursin
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# build model

def build(i):
    """

    Input:  {
              model_name            - model name
              (model_file)          - model output file, otherwise generated as tmp file

              model_params          - dict with model params

              features_table        - features table (in experiment module format)
              features_keys         - features flat keys 
              characteristics_table - characteristics table (in experiment module format)
              characteristics_keys  - characteristics flat keys

              (keep_temp_files)     - if 'yes', keep temp files 
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              model_file       - output model file 
            }

    """

    import tempfile
    import os
    import pickle

    o=i.get('out','')

    mn=i['model_name']
    mp=i.get('model_params',{})

    mf=i.get('model_file','')
    mf1=i['model_file']+'.model.obj'
    mf2=i['model_file']+'.model.dot'
    mf2x=i['model_file']+'.modelx.dot'
    mf3=i['model_file']+'.model.pdf'
    mf4=i['model_file']+'.model.ft.txt'
    mf5=i['model_file']+'.model.inp.ft.json'
    mf6=i['model_file']+'.model.inp.char.json'
    mf7=i['model_file']+'.model.decision_tree.json'

    ftable=i['features_table']
    fkeys=i['features_keys']
    fdesc=i.get('features_desc',{})
    ctable=i['characteristics_table']
    ckeys=i['characteristics_keys']

    lftable=len(ftable)
    lctable=len(ctable)

    # Enumerate features and subsitute in file
    s=''

    fk=0
    for fx in fkeys:
        uu1='X['+str(fk)+']'
        uu2=fdesc.get(fx,{}).get('name','')

        s+=uu1+' '+fx+' ('+uu2+')'
        s+='\n'
        fk+=1

    if s!='':
       r=ck.save_text_file({'text_file':mf4, 'string':s})
       if r['return']>0: return r

    if o=='con':
       ck.out('*******************************************************')
       ck.out('Feature key convertion:')
       ck.out('')
       ck.out(s)

    if lftable!=lctable:
       return {'return':1, 'error':'length of feature table ('+str(lftable)+'is not the same as length of characteristics table ('+str(lctable)+')'}

#    if len(ckeys)>1:
#       return {'return':1, 'error':'currently we support only modeling for 1 characteristic'}

    ktf=i.get('keep_temp_files','')

    # Convert categorical features to floats
    r=convert_categories_to_floats({'table':ftable})
    if r['return']>0: return r

    fconv=r['conv']
    fconv1=r['conv1']
    ftable1=r['table']

    # Prepare (temporary) out model file
    fn2=mf
    if fn2=='' or i.get('web','')=='yes':
       fd2, fn2=tempfile.mkstemp(suffix='.tmp', prefix='ck-')
       os.close(fd2)
       os.remove(fn2)
    else:
       fn2=mf1
       if os.path.isfile(fn2): os.remove(fn2)

    # Remove old files
    if os.path.isfile(mf1): os.remove(mf1)
    if os.path.isfile(mf2): os.remove(mf2)
    if os.path.isfile(mf2x): os.remove(mf2x)
    if os.path.isfile(mf3): os.remove(mf3)
    if os.path.isfile(mf5): os.remove(mf5)
    if os.path.isfile(mf6): os.remove(mf6)
    if os.path.isfile(mf7): os.remove(mf7)

    #############################################################
    if mn=='dtc' or mn=='dtr':
       # http://scikit-learn.org/stable/modules/tree.html
       # http://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
       from sklearn import tree

       pmd=mp.get('max_depth',None)
       pmln=mp.get('max_leaf_nodes',None)

       if mn=='dtc':
          clf = tree.DecisionTreeClassifier(max_depth=pmd, max_leaf_nodes=pmln)
       else:
          clf = tree.DecisionTreeRegressor(max_depth=pmd, max_leaf_nodes=pmln)

       clf = clf.fit(ftable1, ctable)

       r=ck.save_json_to_file({'json_file':mf5, 'dict':ftable1})
       if r['return']>0: return r
       r=ck.save_json_to_file({'json_file':mf6, 'dict':ctable})
       if r['return']>0: return r

       # Save as Graphviz dot
       # dot -Tpdf iris.dot -o iris.pdf.
       with open(mf2, 'w') as f:
          f=tree.export_graphviz(clf, out_file=f)

       # Convert to decision tree
       r=ck.access({'action':'convert_to_decision_tree',
                    'module_uoa':cfg['module_deps']['graph.dot'],
                    'input_file':mf2,
                    'output_file':mf7})
       if r['return']>0: return r

       # Substitute features with names
       import shutil
       shutil.copyfile(mf2,mf2x)
       fk=0
       for fx in fkeys:
           uu1='X['+str(fk)+']'
           uu2=fdesc.get(fx,{}).get('name','')
           r=ck.substitute_str_in_file({'filename':mf2, 'string1':uu1, 'string2':uu1+': '+uu2})
           if r['return']>0: return r
           fk+=1

       # Save as pdf
       s='dot -Tpdf '+mf2+' -o '+mf3
       os.system(s)

#       from sklearn.externals.six import StringIO  
#       import pydot 
#       dot_data = StringIO() 
#       tree.export_graphviz(clf, out_file=dot_data) 
#       graph = pydot.graph_from_dot_data(dot_data.getvalue()) 
#       graph.write_pdf(mf3) 

    else:
       return {'return':1, 'error':'model name '+mn+' is not found in module model.sklearn'}

    # Dump object
    f=open(fn2, 'wb')
    pickle.dump(clf, f, pickle.HIGHEST_PROTOCOL)
    f.close()

    return {'return':0, 'model_file':fn2}

##############################################################################
# validate model

def validate(i):
    """

    Input:  {
              model_name            - model name:
                                                  earth
                                                  lm
                                                  nnet
                                                  party
                                                  randomforest
                                                  rpart
                                                  svm

              model_file            - file with model (object) code

              features_table        - features table (in experiment module format)
              features_keys         - features flat keys 

              (keep_temp_files)     - if 'yes', keep temp files 
            }

    Output: {
              return           - return code =  0, if successful
                                             >  0, if error
              (error)          - error text if return > 0

              prediction_table - experiment table with predictions
            }

    """

    import os
    import pickle

    mn=i['model_name']
    mf=i['model_file']
    mf1=i['model_file']+'.model.obj'
    mf7=i['model_file']+'.model.decision_tree.json'
    mf8=i['model_file']+'.labels.csv'

    ftable=i['features_table']
    fkeys=i['features_keys']

    ktf=i.get('keep_temp_files','')

    lftable=len(ftable)

    # Convert categorical features to floats
    r=convert_categories_to_floats({'table':ftable})
    if r['return']>0: return r

    fconv=r['conv']
    fconv1=r['conv1']
    ftable1=r['table']

    # Load model object
    f=open(mf1, 'rb')
    clf=pickle.load(f)
    f.close()

    sx=''

    #############################################################
    if mn=='dtc' or mn=='dtr':
       from sklearn import tree
       pr=clf.predict(ftable1)

       # Check if CK decision tree file exists
       if os.path.isfile(mf7):
          r=ck.load_json_file({'json_file':mf7})
          if r['return']>0: return r
          labels=r['dict']

          prx=[]
          q=-1
          mtable=i.get('mtable',[])
          for ft in ftable1:
              q+=1
              found=False
              value=False
              for label in labels:
                  p=labels[label]
                  dd=p['decision']
                  dv=p['value']
                  skip=False
                  for k in range(0,len(dd),2):
                      x=dd[k]
                      y=dd[k+1]
                      yc=y['comparison']
                      yf=int(y['feature'])
                      yv=float(y['value'])

                      if yc!='<=': return {'return':1, 'error':'not yet supported condition '+yc+' in decision tree'}

                      if x=='':
                         if not ft[yf]<=yv: skip=True
                      else: 
                         if ft[yf]<=yv: skip=True

                      if skip: break
                  
                  if not skip: 
                     found=True
                     if dv=='true': value=True
                     else: value=False
                     break

              if not found:
                 return {'return':1, 'error':'decision tree is incomplete'}

#              print '**********'
#              for z in range(0, len(ftable1[q])):
#                  zx=ftable1[q][z]
#                  print 'X['+str(z)+']='+str(zx)


              kk=mtable[q].get('features',{}).get('features',{})

              sx+=label+';'+str(dv)
              sx+=';'+str(kk["derived_type_of_prog"])
              sx+=';'+str(kk["type"])
              sx+=';'+str(kk["test"])
              sx+=';'+str(kk["test_id"])
              sx+=';'+str(kk["version"])
              sx+=';'+str(kk["compression"])
              sx+=';'+str(kk["derived_samples_by_primitives"])
              sx+=';'+str(kk["resolution"])
              sx+=';'+str(kk["resw"])
              sx+=';'+str(kk["resx"])
              sx+=';'+str(kk["resy"])

              sx+='\n'

       r=ck.save_text_file({'text_file':mf8, 'string':sx})
       if r['return']>0: return r
    else:
       return {'return':1, 'error':'model name '+mn+' is not found in module model.sklearn'}

    pr1=[]
    for q in pr:
        pr1.append([q])

    return {'return':0, 'prediction_table':pr1}

##############################################################################
# Convert categorical values to floats

def convert_categories_to_floats(i):
    """
    Input:  {
              table - table
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              table - updated table
              conv  - conversion table
              conv1 - conversion numbers
            }

    """

    import sys
    pv2=False
    if sys.version_info[0]<3: pv2=True

    table=i['table']

    # Convert categorical features to floats
    fl=0 # length of feature vector
    conv={}
    conv1={}
    table1=[]

    if len(table)>0: fl=len(table[0])

    if fl>0:
       for k in table:
           vec=[]
           for j in range(0, fl):
               js=str(j)
               jj=k[j]
               if type(jj)==str or (pv2 and type(jj)==unicode):
                  if js not in conv:
                     jx=0.0
                     conv[js]={}
                     conv[js][jj]=jx
                     conv1[js]=jx+1
                     jj=jx
                  else:
                     if jj in conv[js]:
                        jj=conv[js][jj]
                     else:
                        jx=conv1[js]
                        conv[js][jj]=jx
                        jj=jx

                        jx+=1
                        conv1[js]=jx

               vec.append(jj)
           table1.append(vec)

    return {'return':0, 'table':table1, 'conv':conv, 'conv1':conv1}