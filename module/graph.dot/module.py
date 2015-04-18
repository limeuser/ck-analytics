#
# Collective Knowledge (dealing with .dot graph files)
#
# See CK LICENSE.txt for licensing details
# See CK Copyright.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://cTuning.org/lab/people/gfursin
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
# converting .dot file made by machine learning algorithms to active decision tree

def convert_to_decision_tree(i):
    """
    Input:  {
              input_file  - .dot file
              output_file - CK json decision tree file

            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              labels
              decisions
              link_yes
              link_no
            }

    """

    fi=i['input_file']
    fo=i['output_file']

    s=''
    r=ck.load_text_file({'text_file':fi, 
                         'split_to_list':'yes'})
    if r['return']>0: return r
    lst=r['lst']

    jl=1
    labels={}
    kl=1
    decisions={}
    link={}
    link_yes={}
    link_no={}

    # Detecting all labels (leafs) and decisions
    for j in range(0, len(lst)):
        q=lst[j]

        ll=''
        j1=q.find(' ')
        if j1>0:
           ll=q[:j1].strip()

        j0=q.find('\\nvalue = [')
        if j0>0:
           j2=q.find('[label="')
           if j2>0:
              sjl=str(jl)
              lst[j]=q[:j2+8]+'*L'+sjl+'*\\n'+q[j2+8:]

              labels[sjl]={'dot_label':ll}

              j3=q.find(']',j0+1)
              vals=q[j0+11:j3].strip()
              j4=vals.find(' ')

              v0=vals[:j4].strip()
              v1=vals[j4+1:].strip()

              if v0.endswith('.'): v0=int(v0[:-1])
              if v1.endswith('.'): v1=int(v1[:-1])

              if v0>v1: value=False
              else: value=True

              labels[sjl]['value']=value

              jl+=1

        else:
           j1=q.find('[label="')
           if j1>0:
              j2=q.find('\\n',j1+1)
              j3=q.find(']',j1+1)
              j4=q.find(' ',j1+1)
              j5=q.find(' ',j4+1)

              dx={}
              dx['feature']=q[j1+10:j3]
              dx['comparison']=q[j4+1:j5]
              dx['value']=q[j5+1:j2]

              j1=q.find(' ')
              l1=q[:j1].strip()
             
              decisions[ll]=dx

           j1=q.find(' -> ')
           if j1>0:
              j2=q.find(';', j1+1)
              ll2=q[j1+4:j2].strip()

              if ll in link: 
                 link_no[ll2]=ll
              else:
                 link[ll]='+'
                 link_yes[ll2]=ll

        s+=lst[j]+'\n'

    # Finding path to a given leaf
    for ll in labels:
        l=labels[ll]

        dl=l['dot_label']

        dt=[]

        lx=dl
        value=''
        while lx!='0':
           x=''
           if lx in link_yes:
              lx=link_yes[lx]
           else:
              lx=link_no[lx]
              x='not '

           dt.append(x)
           dt.append(decisions[lx])

        # reverse for top bottom check
        dt1=[]
        ldt=len(dt)
        for q in range(0, ldt, 2):
            dt1.append(dt[ldt-q-2])
            dt1.append(dt[ldt-q-1])

        l['decision']=dt1

    # Save labels + decisions file
    r=ck.save_json_to_file({'json_file':fo, 'dict':labels})
    if r['return']>0: return r

    # Update .dot file
    r=ck.save_text_file({'text_file':fi, 'string':s})
    if r['return']>0: return r

    return {'return':0, 'labels':labels, 'decisions':decisions, 'link_yes':link_yes, 'link_no':link_no}