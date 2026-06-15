import fiatlight as fl
from fiatlight.fiat_kits.fiat_ai import Prompt


"""Test that we can comfortably edit and display a multi-line string with different layouts
depending on whether we are in a node or in a detached window."""

poem = """Demain, dès l'aube, à l'heure où blanchit la campagne,
Je partirai. Vois-tu, je sais que tu m'attends.
J'irai par la forêt, j'irai par la montagne.
Je ne puis demeurer loin de toi plus longtemps.

Je marcherai les yeux fixés sur mes pensées,
Sans rien voir au dehors, sans entendre aucun bruit,
Seul, inconnu, le dos courbé, les mains croisées,
Triste, et le jour pour moi sera comme la nuit.

Je ne regarderai ni l'or du soir qui tombe,
Ni les voiles au loin descendant vers Harfleur,
Et quand j'arriverai, je mettrai sur ta tombe
Un bouquet de houx vert et de bruyère en fleur.

Victor Hugo, extrait du recueil «Les Contemplations» (1856)
        """


@fl.with_fiat_attributes(
    multiline_text__multiline=True,
)
def f(short_input: str, multiline_text: str = poem, prompt: Prompt = Prompt("A cat on the moon")) -> tuple[str, str]:
    return short_input, multiline_text


def c(s: str) -> int:
    """Count the number of lines in a string."""
    return len(s.splitlines())


if __name__ == "__main__":
    graph = fl.FunctionsGraph().from_function_composition([f, c])
    graph.add_function(c)

    fl.run(graph, app_name="Multiline string usability test")
