"""Usability example of a Markdown node

Some lines of the poem should be wrapped to the next line,
to show the effect of the text width parameter.

At the moment links will only work when viewed in the detached window.
"""

import fiatlight as fl

# Notes:
# In order to force a line break, you should use two spaces at the end of the line.
# the Markdown renderer does not support HTML!
#
# Below we are using _br_, as a workaround around pre-commit
# which does not allow trailing spaces in the code.
md_string = """
> **Paul Verlaine**_br_
> Paul-Marie Verlaine (30 March 1844 - 8 January 1896) was a French poet associated with the [Symbolist](https://en.wikipedia.org/wiki/Symbolist) movement and the [Decadent movement](https://en.wikipedia.org/wiki/Decadent_movement). He is considered one of the greatest representatives of the [fin de siècle](https://en.wikipedia.org/wiki/Fin_de_si%C3%A8cle) in international and French poetry.

# Mon rêve familier_br_
_br_
> Paul Verlaine_br_
_br_
Je fais souvent ce rêve étrange et pénétrant_br_
D'une femme inconnue, et que j'aime, et qui m'aime_br_
Et qui n'est, chaque fois, ni tout à fait la même_br_
Ni tout à fait une autre, et m'aime et me comprend._br_
_br_
Car elle me comprend, et mon coeur transparent_br_
Pour elle seule, hélas! cesse d'être un problème_br_
Pour elle seule, et les moiteurs de mon front blême,_br_
Elle seule les sait rafraîchir, en pleurant._br_
_br_
Est-elle brune, blonde ou rousse? Je l'ignore._br_
Son nom? Je me souviens qu'il est doux et sonore,_br_
Comme ceux des aimés que la vie exila._br_
_br_
Son regard est pareil au regard des statues,_br_
Et, pour sa voix, lointaine, et calme, et grave, elle a_br_
L'inflexion des voix chères qui se sont tues._br_
_br_
Paul Verlaine, *Poèmes saturniens*
"""
md_string = md_string.replace("_br_", "  ")

graph = fl.FunctionsGraph()
graph.add_markdown_node(md_string, label="Mon rêve familier", text_width_em=20)
fl.run(graph)
