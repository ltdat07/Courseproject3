from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest

from app.course_content import TOPICS
from app.practice_content import TASKS


class CSharpExamplesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dotnet = shutil.which("dotnet")
        if not cls.dotnet:
            raise unittest.SkipTest("Для компиляции примеров нужен .NET SDK 8 или новее.")
        listing = subprocess.run(
            [cls.dotnet, "--list-sdks"], capture_output=True, text=True, check=True, timeout=15,
        ).stdout
        sdks = re.findall(r"^(\d+\.\d+\.\S+) \[(.+)\]$", listing, re.MULTILINE)
        sdks = [(version, Path(folder)) for version, folder in sdks if int(version.split('.')[0]) >= 8]
        if not sdks:
            raise unittest.SkipTest("Для компиляции примеров нужен .NET SDK 8 или новее.")
        version, folder = sdks[-1]
        cls.compiler = folder / version / "Roslyn" / "bincore" / "csc.dll"
        major = version.split('.')[0]
        packs = folder.parent / "packs" / "Microsoft.NETCore.App.Ref"
        references = sorted(packs.glob(f"{major}.*/ref/net{major}.0"))
        if not references:
            raise unittest.SkipTest("Не найдены стандартные библиотеки .NET SDK.")
        cls.references = list(references[-1].glob("*.dll"))

    def test_class_and_interface_examples_compile(self):
        snippets = {}
        for topic_id in [5, 11]:
            topic = next(item for item in TOPICS if item["id"] == topic_id)
            snippets[f"topic-{topic_id}"] = re.search(
                r"```csharp\s*\n(.*?)```", topic["theory"], re.DOTALL,
            ).group(1)
        snippets["task-13"] = next(item["code"] for item in TASKS if item["id"] == 13)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name, code in snippets.items():
                with self.subTest(example=name):
                    source = root / f"{name}.cs"
                    source.write_text("using System;\n" + code, encoding="utf-8")
                    arguments = ["/nologo", "/utf8output", "/target:exe", f'/out:"{root / (name + ".dll")}"']
                    arguments.extend(f'/reference:"{path}"' for path in self.references)
                    arguments.append(f'"{source}"')
                    response_file = root / "compile.rsp"
                    response_file.write_text("\n".join(arguments), encoding="utf-8")
                    result = subprocess.run(
                        [self.dotnet, str(self.compiler), "@" + str(response_file)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
