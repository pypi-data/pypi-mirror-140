def changeLogic(operator: str):
    if operator.lower().strip() == "and":
        return "&"
    if operator.lower().strip() == "or":
        return "|"

class Cell:
    def __init__(self, cell: dict):
        self.query = []
        for attribute in cell.attributes:
            try:
                self.query.append(
                    f'({eval("self."+attribute.op.lower()+"(attribute)")})'
                )
            except IndexError:
                pass
            except AttributeError:
                pass
            self.query.append(
                changeLogic(attribute.condition)
                if hasattr(attribute, "condition")
                else changeLogic("and")
            )

    def between(self, item):
        return f"(df_ref.{item.id} >= {item.value[0]}) & (df_ref.{item.id} <= {item.value[1]})"

    def greater_then(self, item):
        return f"df_ref.{item.id} >= {item.value}"

    def less_than(self, item):
        return f"df_ref.{item.id} <= {item.value}"

    def equals(self, item):
        if isinstance(item.value, list):
            query = []
            for value in item.value:
                query.append(f"(df_ref.{item.id} == '{value}')")
            return " | ".join(query)
        elif item.value in ['True', 'False']:
            return f"df_ref.{item.id} == {'1' if item.value == 'True' else '0'}"
        else:
            return f"df_ref.{item.id} == {item.value}"

    def not_equals(self, item):
        if isinstance(item.value, list):
            query = []
            for value in item.value:
                query.append(f"(df_ref.{item.id} != '{value}')")
            return " | ".join(query)
        elif item.value in ['True', 'False']:
            return f"df_ref.{item.id} == {'0' if item.value == 'True' else '1'}"
        else:
            return f"df_ref.{item.id} != {item.value}"


def query_build(query):
    final_query = []
    for item in query:
        final_query.append(f"({' '.join(Cell(item).query[:-1]).strip()})")
        final_query.append(f"{changeLogic(item.op)}")
    return " ".join(final_query[:-1]).strip()
