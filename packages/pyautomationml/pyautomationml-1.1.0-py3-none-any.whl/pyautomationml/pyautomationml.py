import os
import sys
import lxml.objectify as ob
import lxml.etree as et


def Element(tag, attrib=None, text=None, context_global=None, context_local=None):
    E = ob.ElementMaker(annotate=False)
    return AmlElement(E(tag, text, attrib), context_global, context_local)


class AmlElement:
    def __init__(self, element, context_global, context_local, lookup_by_name=False):
        self.__lookup_by_name__ = lookup_by_name
        self.__element__ = element
        self.__context_local__ = context_local
        self.__context_global__ = context_global

    def __getattr__(self, key):
        if key == "fun":
            self.__context_local__.update({"ancestors": self.iterancestors()})
            result = eval(self.text().strip(), self.__context_global__, self.__context_local__)
            self.__context_local__.pop("ancestors")
        else:
            if self.__lookup_by_name__:
                result = self.find(f"./*[@Name='{key}']")
                if result is None:
                    result = self.__element__.__getattribute__(key)
                    if isinstance(result, ob.ObjectifiedElement):
                        raise AttributeError(f"No such child: {key}")
            else:
                result = self.__element__.__getattribute__(key)
            if isinstance(result, ob.ObjectifiedElement):
                result = AmlElement(result, self.__context_global__, self.__context_local__, self.__lookup_by_name__)
        return result

    def __setattr__(self, key, value):
        if key in ("__element__", "__context_local__", "__context_global__", "__lookup_by_name__"):
            self.__dict__[key] = value
        else:
            if isinstance(value, AmlElement):
                value = value.__element__
            if self.__lookup_by_name__:
                element = self.find(f"./*[@Name='{key}']")
                if element is not None:
                    tag = element.tag
                    element.clear()
                    self.__element__.__setattr__(tag, value)
            else:
                self.__element__.__setattr__(key, value)

    def __repr__(self):
        return f"<AmlElement object {self.__element__.tag} Name={self.__element__.get('Name')}>"

    def iterancestors(self):
        return [AmlElement(i, self.__context_global__, self.__context_local__, self.__lookup_by_name__) for i in [self.__element__] + list(self.__element__.iterancestors())]

    def iterchildren(self):
        result = self.__element__.iterchildren()
        return [AmlElement(i, self.__context_global__, self.__context_local__, self.__lookup_by_name__) for i in result] if result is not None else None

    def find(self, path):
        result = self.__element__.find(path)
        return AmlElement(result, self.__context_global__, self.__context_local__, self.__lookup_by_name__) if result is not None else None

    def findall(self, path):
        result = self.__element__.findall(path)
        return [AmlElement(i, self.__context_global__, self.__context_local__, self.__lookup_by_name__) for i in result] if result is not None else None

    def get_element_by_id(self, id):
        return self.find(f".//*[@ID='{id}']")

    def get_linked_interface(self):
        if self.tag == "ExternalInterface":
            ancestors = self.iterancestors()
            id = ancestors[1].find(f"./InternalLink[@RefPartnerSideA='{self.get('ID')}']").get("RefPartnerSideB")
            return ancestors[-1].find(f".//ExternalInterface[@ID='{id}']")
        else:
            return None

    def text(self):
        return self.__element__.Value.text


class PyAutomationML:
    def __init__(self, source_file):
        self.source_file = source_file
        self.context_local = {}
        self.context_global = {}
        self.root = AmlElement(ob.parse(self.source_file).getroot(), self.context_global, self.context_local)

    def eval(self, verbose=False):
        evaluated = 0
        not_evaluated = 0
        errors = 0
        lookup_cfg = self.root.__lookup_by_name__
        self.root.__lookup_by_name__ = True
        preamble = self.root.find("./InstanceHierarchy//InternalElement[@Name='PythonPreamble']").Content

        if preamble is not None:
            self.context_local.update({"ancestors": preamble.iterancestors()})
            try:
                exec(preamble.text().strip(), self.context_global, self.context_local)
            except Exception as e:
                if verbose:
                    print("Error in line {0} in file {1}\n          {2} \n{3}\n".format(preamble.sourceline + 1, self.source_file, preamble.text(), e), file=sys.stderr)
            else:
                if verbose:
                    print("Context from Python preamble successfully created", file=sys.stderr)
            self.context_local.pop("ancestors")
        else:
            if verbose:
                print("No Python preamble found continuing with builtin context", file=sys.stderr)

        expression_elements = self.root.findall("./InstanceHierarchy//Attribute[@RefAttributeType='PyAMLLib/PythonExpression']")
        for element in expression_elements:
            self.context_local.update({"ancestors": element.iterancestors()})
            try:
                result = eval(element.text().strip(), self.context_global, self.context_local)
            except Exception as e:
                errors += 1
                if verbose:
                    print("Error in line {0} in file {1}\n          {2} \n{3}\n".format(element.sourceline+1, self.source_file, element.text(), e), file=sys.stderr)
            else:
                if not callable(result):
                    evaluated += 1
                    element.__element__.Value._setText(str(result))
                else:
                    not_evaluated += 1
            self.context_local.pop("ancestors")

        self.root.__context_local__ = self.context_local
        self.root.__context_global__ = self.context_global
        self.root.__lookup_by_name__ = lookup_cfg

        if verbose:
            print("{0} total PythonExpression{1} found".format(len(expression_elements), "s" if len(expression_elements) > 1 else ""), file=sys.stderr)
            print("{0} PythonExpression{1} successfully instantiated as literals.".format(evaluated, "s" if evaluated > 1 else ""), file=sys.stderr)
            print("{0} PythonExpression{1} could not be instantiated as literal{2} because {3} functions.".format(
                not_evaluated, "s" if not_evaluated > 1 else "", "s" if not_evaluated > 1 else "", "they are" if not_evaluated > 1 else "it is a"), file=sys.stderr)
            if errors:
                print("{0} PythonExpression{1} could not be instantiated because of errors.".format(
                    errors, "s" if errors > 1 else ""), file=sys.stderr)

    def save(self, filename=None):
        if not filename:
            old_filename, file_extension = os.path.splitext(self.source_file)
            filename = old_filename + "_instantiated" + file_extension
        with open(filename, "wb") as file:
            file.write(et.tostring(self.root.__element__, pretty_print=True))
