# -*- coding: utf-8 -*-
import re

from transkribus.xml import XmlElement

NAMESPACES = {
    "page": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15",
}

CSS_RULES_REGEX = re.compile(r"(\S+)\s*{([^}]+)}")
CSS_PROPERTIES_REGEX = re.compile(r"(\S+?):\s*(\S+?);")


class Tag(object):
    def __init__(self, name, value):
        self.name = name
        if isinstance(value, dict):
            self.__dict__.update(value)
        for match in CSS_PROPERTIES_REGEX.finditer(value):
            prop_name, prop_value = match.groups()
            # Some special characters are escaped using \uXXXX; this unescapes them
            prop_value = prop_value.encode("latin1").decode("unicode_escape")
            setattr(self, prop_name, prop_value)

    def as_dict(self):
        return self.__dict__

    @classmethod
    def build(cls, text):
        if not text:
            return []
        tags = []
        for match in CSS_RULES_REGEX.finditer(text):
            tags.append(cls(*match.groups()))
        return tags


class PageXmlElement(XmlElement):
    def __init__(self, path, namespaces=NAMESPACES):
        super().__init__(path, namespaces=namespaces)
        assert (
            self.element.nsmap.get("page") == self.namespaces["page"]
            or self.element.nsmap.get(None) == self.namespaces["page"]
        ), "Missing tei XML namespace"


class Region(PageXmlElement):
    optional = ("custom",)

    def get_points(self, path):
        text = self._find(path)
        if text is None:
            return
        points = []
        for coords in filter(None, map(str.strip, text.split(" "))):
            x, y = coords.split(",", 1)
            points.append((int(x), int(y)))
        return points

    def parse(self):
        return {
            "id": self.get_text("@id"),
            "points": self.get_points("page:Coords/@points"),
            "tags": Tag.build(self.get_text("@custom")),
        }


class TextLine(Region):
    optional = Region.optional + ("confidence",)

    def parse(self):
        data = super().parse()
        data.update(
            text=self.get_text("page:TextEquiv/page:Unicode"),
            baseline=self.get_points("page:Baseline/@points"),
            confidence=self.get_float("page:TextEquiv/@conf"),
        )
        return data


class TextRegion(Region):
    optional = Region.optional + ("type", "confidence")

    def parse(self):
        data = super().parse()
        data.update(
            type=self.get_text("@type"),
            text=self.get_text("page:TextEquiv/page:Unicode"),
            confidence=self.get_float("page:TextEquiv/@conf"),
            lines=self.get_instance(TextLine, "page:TextLine", many=True),
        )
        return data


class PageElement(PageXmlElement):
    optional = ("type",)

    def get_ordering(self):
        return [
            ref.get("regionRef")
            for ref in sorted(
                self._find(
                    "page:ReadingOrder/page:OrderedGroup/page:RegionRefIndexed",
                    many=True,
                ),
                key=lambda elt: int(elt.get("index")),
            )
        ]

    def get_relations(self):
        relations = []
        for relation in self._find(
            'page:Relations/page:Relation[@type="link"]', many=True
        ):
            refs = relation.findall("page:RegionRef", namespaces=self.namespaces)
            assert (
                len(refs) >= 2
            ), "Expected at least two regions in relation, got {}".format(len(refs))
            relations.append([ref.get("regionRef") for ref in refs])
        return relations

    def parse(self):
        return {
            "image_name": self.get_text("@imageFilename"),
            "image_width": self.get_text("@imageWidth"),
            "image_height": self.get_text("@imageHeight"),
            "type": self.get_text("@type"),
            "text_regions": self.get_instance(TextRegion, "page:TextRegion", many=True),
            "unknown_regions": self.get_instance(
                Region, "page:UnknownRegion", many=True
            ),
            # TODO? MusicRegion, NoiseRegion, TableRegion, SeparatorRegion
            "ordering": self.get_ordering(),
            "relations": self.get_relations(),
        }

    def sort_regions(self, regions):
        if len(regions) <= 1 or not self.ordering:
            return regions
        return sorted(
            regions,
            key=lambda region: self.ordering.index(region.id)
            if region.id in self.ordering
            else 0,
        )


class PageXmlMetadata(PageXmlElement):
    optional = ("comments",)

    def parse(self):
        return {
            "creator": self.get_text("page:Creator"),
            "created": self.get_text("page:Created"),
            "last_change": self.get_text("page:LastChange"),
            "comments": self.get_text("page:Comments"),
        }


class PageXmlPage(PageXmlElement):
    def parse(self):
        return {
            "metadata": self.get_instance(PageXmlMetadata, "page:Metadata"),
            "page": self.get_instance(PageElement, "page:Page"),
        }
