
from pathlib import Path
from tempfile import TemporaryDirectory

from rdflib import Graph, Namespace, RDF
from owlready2 import World, sync_reasoner
from owlready2.base import OwlReadyInconsistentOntologyError


ROOT = Path(__file__).resolve().parent
ONTO_FILE = ROOT / "models" / "onto.owl"
DATA_FILE = ROOT / "models" / "onto_data.ttl"
LOG_FILE = ROOT / "docs" / "reasoner_log.md"

BASE = "http://example.org/ecommerce-recommendations#"
EX = Namespace(BASE)


def load_graph():
    """Завантажує онтологію та індивідів в один RDF-граф."""
    graph = Graph()
    graph.parse(str(ONTO_FILE), format="turtle")
    graph.parse(str(DATA_FILE), format="turtle")
    return graph


def run_reasoner(graph, output_file):
    """Зберігає граф в OWL/XML і запускає HermiT."""
    graph.serialize(destination=str(output_file), format="xml")

    world = World()
    onto = world.get_ontology(output_file.as_uri()).load()

    with onto:
        sync_reasoner(
            [onto],
            infer_property_values=True,
            debug=1,
        )

    return world, onto


def get_inferred_types(onto, graph):
    """Повертає виведені класи для customer01."""
    customer = onto.search_one(iri=BASE + "customer01")

    if customer is None:
        return []

    explicit_types = {
        str(obj).rsplit("#", 1)[-1]
        for obj in graph.objects(EX.customer01, RDF.type)
    }

    inferred = set()

    for cls in customer.INDIRECT_is_a:
        iri = getattr(cls, "iri", "")
        name = getattr(cls, "name", None)

        if iri.startswith(BASE) and name:
            if name not in explicit_types:
                inferred.add(name)

    return sorted(inferred)


def error_message(error):
    """Повертає текст помилки або зрозуміле пояснення."""
    message = str(error).strip()

    if message:
        return message

    return (
        "HermiT повідомив про неконсистентність, "
        "але не повернув текстового опису помилки."
    )


def main():
    graph = load_graph()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    log = [
        "# Лабораторна робота 7 — HermiT",
        "",
        "## 1. Перевірка початкової онтології",
        "",
        f"- Кількість RDF-тверджень: {len(graph)}",
        f"- Файл онтології: `{ONTO_FILE.name}`",
        f"- Файл індивідів: `{DATA_FILE.name}`",
        "",
    ]

    with TemporaryDirectory() as temp:
        temp_dir = Path(temp)

        # ЕТАП 1. Перевірка початкової онтології.
        original_file = temp_dir / "original.owl"

        try:
            original_world, original_onto = run_reasoner(
                graph, original_file
            )

            log += [
                "**Результат: CONSISTENT (узгоджена).**",
                "",
                "HermiT завершив перевірку початкової онтології "
                "без помилки узгодженості.",
                "",
                "### Виведені твердження",
                "",
            ]

            inferred = get_inferred_types(original_onto, graph)

            if inferred:
                for class_name in inferred:
                    log.append(
                        f"- `:customer01 rdf:type :{class_name}`"
                    )
            else:
                log.append(
                    "Не отримано нових типів для customer01. "
                    "Перевірте результат класифікації онтології."
                )

            log += [
                "",
                "### Правила успадкування",
                "",
                "- `Customer rdfs:subClassOf Agent`",
                "- `Agent rdfs:subClassOf KnowledgeEntity`",
                "- `KnowledgeEntity rdfs:subClassOf TopLevelEntity`",
                "",
                "Ці зв'язки пояснюють, чому reasoner може "
                "вивести додаткові типи для customer01.",
                "",
            ]

        except OwlReadyInconsistentOntologyError as error:
            log += [
                "**Результат: INCONSISTENT (неконсистентна).**",
                "",
                "Початкова онтологія містить суперечність.",
                "",
                "```text",
                error_message(error),
                "```",
                "",
            ]

        # ЕТАП 2. Додавання навмисної суперечності.
        log += [
            "## 2. Перевірка навмисної суперечності",
            "",
            "До тимчасової копії графа додається твердження "
            "`:customer01 a :Product`.",
            "",
            "У початкових даних customer01 належить до класу "
            "`Customer`. Якщо `Customer` і `Product` оголошені "
            "диз'юнктними, reasoner має виявити суперечність.",
            "",
        ]

        broken_graph = Graph()

        for triple in graph:
            broken_graph.add(triple)

        broken_graph.add(
            (EX.customer01, RDF.type, EX.Product)
        )

        broken_file = temp_dir / "contradiction.owl"

        try:
            broken_world, broken_onto = run_reasoner(
                broken_graph, broken_file
            )

            log += [
                "**Результат: суперечність не виявлено.**",
                "",
                "Перевірте, чи класи `Customer` і `Product` "
                "оголошені диз'юнктними в `onto.owl`.",
                "",
            ]

        except OwlReadyInconsistentOntologyError as error:
            log += [
                "**Результат: INCONSISTENT (неконсистентна).**",
                "",
                "HermiT виявив суперечність після додавання "
                "твердження `:customer01 a :Product`.",
                "",
                "Причина: `customer01` належить до класів "
                "`Customer` і `Product`, які мають бути "
                "оголошені диз'юнктними.",
                "",
                "### Повідомлення reasoner",
                "",
                "```text",
                error_message(error),
                "```",
                "",
            ]

        # ЕТАП 3. Повторна перевірка початкових даних.
        log += [
            "## 3. Усунення суперечності",
            "",
            "Суперечливе твердження було додане тільки до "
            "тимчасової копії графа. Файл `onto_data.ttl` "
            "не змінювався.",
            "",
            "Для усунення суперечності використовуються "
            "початкові дані без додаткового твердження.",
            "",
        ]

        try:
            restored_file = temp_dir / "restored.owl"

            restored_world, restored_onto = run_reasoner(
                graph, restored_file
            )

            log += [
                "**Результат: CONSISTENT (узгоджена).**",
                "",
                "Повторна перевірка початкової онтології "
                "завершилася без помилки узгодженості.",
                "",
            ]

        except OwlReadyInconsistentOntologyError as error:
            log += [
                "**Результат: INCONSISTENT (неконсистентна).**",
                "",
                "Початкові дані все ще містять суперечність.",
                "",
                "```text",
                error_message(error),
                "```",
                "",
            ]

    LOG_FILE.write_text(
        "\n".join(log) + "\n",
        encoding="utf-8",
    )

    print(LOG_FILE.read_text(encoding="utf-8"))
    print(f"\nЛог збережено: {LOG_FILE}")


if __name__ == "__main__":
    main()
