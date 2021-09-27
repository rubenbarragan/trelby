from lxml import etree
import util
import screenplay
import misc

# CLI to convert file formats.

def importFDX(fileName):
    elemMap = {
        "Action" : screenplay.ACTION,
        "Character" : screenplay.CHARACTER,
        "Dialogue" : screenplay.DIALOGUE,
        "Parenthetical" : screenplay.PAREN,
        "Scene Heading" : screenplay.SCENE,
        "Shot" : screenplay.SHOT,
        "Transition" : screenplay.TRANSITION,
    }

    # the 5 MB limit is arbitrary, we just want to avoid getting a
    # MemoryError exception for /dev/zero etc.
    data = util.loadFile(fileName, 5000000)

    if data == None:
        return None

    if len(data) == 0:
        return None

    try:
        root = etree.XML(data)
        lines = []

        def addElem(eleType, eleText):
            lns = eleText.split("\n")

            # if elem ends in a newline, last line is empty and useless;
            # get rid of it
            if not lns[-1] and (len(lns) > 1):
                lns = lns[:-1]

            for s in lns[:-1]:
                lines.append(screenplay.Line(
                        screenplay.LB_FORCED, eleType, util.cleanInput(s)))

            lines.append(screenplay.Line(
                    screenplay.LB_LAST, eleType, util.cleanInput(lns[-1])))

        for para in root.xpath("Content//Paragraph"):
            addedNote = False
            et = para.get("Type")

            # Check for script notes
            s = ""
            for notes in para.xpath("ScriptNote/Paragraph/Text"):
                if notes.text:
                    s += notes.text

                # FD has AdornmentStyle set to "0" on notes with newline.
                if notes.get("AdornmentStyle") == "0":
                    s += "\n"

            if s:
                addElem(screenplay.NOTE, s)
                addedNote = True

            # "General" has embedded Dual Dialogue paragraphs inside it;
            # nothing to do for the General element itself.
            #
            # If no type is defined (like inside scriptnote), skip.
            if (et == "General") or (et is None):
                continue

            s = ""
            for text in para.xpath("Text"):
                # text.text is None for paragraphs with no text, and +=
                # blows up trying to add a string object and None, so
                # guard against that
                if text.text:
                    s += text.text

            # don't remove paragraphs with no text, unless that paragraph
            # contained a scriptnote
            if s or not addedNote:
                lt = elemMap.get(et, screenplay.ACTION)
                addElem(lt, s)

        if len(lines) == 0:
            return None

        return lines

    except etree.XMLSyntaxError as e:
        return None

util.init(False)
misc.init(False)

fdx = importFDX("/Users/rbarragan/Downloads/fdx_files/AMC Theatres Commercial.fdx")

for line in fdx:
    print(line.text)
