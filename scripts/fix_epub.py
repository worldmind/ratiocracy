import re
from pathlib import Path


regex = re.compile(r'''<a class="glossterm" epub:type="glossterm" href="[^"]+">(<em class="glossterm" epub:type="glossterm"><a class="glossterm" epub:type="glossterm" href="[^"]+" title="[^"]+">[^"]+</a></em>)</a>''')

for f in Path("epub/OEBPS/").glob("*.xhtml"):
    data = f.read_text()
    data = regex.sub(r"\1", data)
    f.write_text(data)
