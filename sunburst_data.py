import plotly.graph_objects as go
import plotly.express as px


#COLOR_MAP 
# one color per possible result of "get_sigma_function" is required
#
color_map = { "Positive": { "root":  "#CCFFCC",
                            "items": px.colors.qualitative.Antique} , #https://plotly.com/python/discrete-color/
              "Negative": { "root":  "#FFCCCC",
                            "items": px.colors.qualitative.Plotly } }
#
# per root-label => colorscale
# label => (optional)) hash inside colorscale to provide deterministic color-selection per label(-text)
#
def get_color(root, label):
    #
    # label not associated with a root-id? => this is a root-item!
    if not root:
      return color_map[label]["root"]
    #
    # use first color in list
    # * rotate list afterwards
    cs = color_map[root]["items"]
    color = cs.pop(0)
    cs.append(color)
    #
    return color


SIGN_MAP = {}
SIGN_MAP[True]="Positive"
SIGN_MAP[False]="Negative"
#
# todo: amount="0" doesn't makes sense in sunburst => exception!?
#
def get_sigma_amount(b):
    #
    return SIGN_MAP[ (b["amount"]>0) ] 

#
#
class SunburstData:
  # sigma = function over dataset returning name/id of root-class
  #
  def __init__(self, get_sigma_function=get_sigma_amount, get_color_function=get_color):
    self.keys=[]    # "ids"
    self.labels=[]
    self.parents=[]
    self.values=[]
    self.hover_names = []
    self.colors = []
    self.get_sigma = get_sigma_function
    self.get_color = get_color_function
    
  def __determine_color(self, parent, key):
    #  
    if parent in self.keys:
        index = self.keys.index(parent)
        # parent has a parent? => not root! use color of parent
        if self.parents[index]:
          return self.colors[index]
    #
    # parent == root? determine color
    return self.get_color(parent, key)
    
    
  # return "key" to be referenced as "parent" for next level in hierarchy
  #  
  def __push(self, value, b, label="", hover="", parent="", uniq=False):
      #
      #no label? => root level
      #
      if not label:
        label = self.get_sigma(b)
      # 
      key = parent+"."+label if parent else label
      #
      # uniq? prepend #counter to generate id
      #
      if uniq:
        key += "#"+str(self.labels.count(label))
      #
      try:
        index = self.keys.index(key)
        self.values[index] += abs(value)
      except:
        self.keys.append(key)
        self.labels.append(label) 
        self.values.append(abs(value))
        self.hover_names.append(hover)
        self.parents.append(parent)
        self.colors.append( self.__determine_color(parent, key) )
      #  
      return key
  
  # struct = list of dictonaries
  # - label (required)
  # - hover (optional)
  #
  def add_item(self, b, struct):
    #
    value = b["amount"]
    #
    #prepare root-level entry 
    # * empty label => sigma-function determines root-level label
    #   e.g.("Haben" | "Soll") or [DBIT|CRDT]
    parent_id = self.__push(value, b, label="", hover="", parent="")
    #
    # last level in hierarchy - label must be (made) uniq
    struct[-1]["uniq"] = True
    #
    # add multi-level hierarchy to root-item
    for s in struct:
      label = s["label"]
      hover = s.get("hover","")
      uniq = s.get("uniq", False)
      parent_id = self.__push(value, b, label=label, hover=hover, parent=parent_id, uniq=uniq)
      
  def get_figure(self, maxdepth=0):
    return go.Figure(go.Sunburst(
         ids=self.keys,
         labels=self.labels,
         parents=self.parents,
         values=self.values,
         hovertext=self.hover_names,
         branchvalues="total",
         marker=dict(colors=self.colors),
         maxdepth=maxdepth
        ))


# demo
#
if __name__ == '__main__':
    sunburst_data = SunburstData()
    
    sunburst_data.add_item( { "amount":10 }, [ {"label":"Class A"},
                                               {"label":"Sub-Class AA"},
                                               {"label":"AA_1", "hover":"first Item in AA"} ]
                          )
    sunburst_data.add_item( { "amount":30 }, [ {"label":"Class A"},
                                               {"label":"Sub-Class AA"},
                                               {"label":"AA_2", "hover":"second Item in AA"} ]
                          )
    sunburst_data.add_item( { "amount":-10 }, [ {"label":"Class A"},
                                                {"label":"Sub-Class AA"},
                                                {"label":"AA_3", "hover":"third Item in AA"} ]
                          )
    sunburst_data.add_item( { "amount":-20 }, [ {"label":"Class B"},
                                                {"label":"Sub-Class BB"},
                                                {"label":"BB_1", "hover":"first Item in BB"} ]
                          )    
    sunburst_data.add_item( { "amount":-5 }, [ {"label":"Class B"},
                                                {"label":"Sub-Class BB"},
                                                {"label":"Sub-Class BBB"},
                                                {"label":"BBB_1", "hover":"first Item in BBB"} ]
                          )    
    sunburst_data.add_item( { "amount":-5 }, [ {"label":"Class B"},
                                                {"label":"Sub-Class BB"},
                                                {"label":"Sub-Class BBB"},
                                                {"label":"BBB_2", "hover":"second Item in BBB"} ]
                          ) 
    #
    fig = sunburst_data.get_figure(maxdepth=5)
    #
    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))
    fig.update_traces(textinfo="label+percent parent")
    fig.show()
    
  