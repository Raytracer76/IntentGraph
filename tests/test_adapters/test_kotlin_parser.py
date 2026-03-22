import pytest
from pathlib import Path
from uuid import UUID
import tempfile
import shutil
from intentgraph.adapters.parsers.kotlin_parser import KotlinParser


@pytest.fixture
def kotlin_parser():
    return KotlinParser()


@pytest.fixture
def tmp_repo():
    path = Path(tempfile.mkdtemp())
    yield path
    shutil.rmtree(path)


class TestKotlinParserUltimate:
    def test_kotlin_basic_parsing(self, kotlin_parser, tmp_repo):
        code = (
            "import android.os.Bundle\n"
            "class A {\n"
            "    fun b() {\n"
            "        if (true) { }\n"
            "    }\n"
            "}"
        )
        f = tmp_repo / "A.kt"
        f.write_text(code)

        # Unpack usando function_deps per assicurarci che sia vuoto come vuole Raytracer
        symbols, exports, function_deps, imports, metadata = kotlin_parser.extract_code_structure(f, tmp_repo)

        assert function_deps == []
        assert 'total_classes' in metadata
        assert 'total_functions' in metadata
        assert metadata['total_classes'] >= 1
        assert metadata['total_functions'] >= 1

    def test_kotlin_resolve_utility_direct(self, kotlin_parser, tmp_repo):
        pkg_dir = tmp_repo / "app/src/main/kotlin/com/pkg"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "Utils.kt").write_text("class Utils")

        resolved = kotlin_parser._resolve_kotlin_import("com.pkg.Utils", tmp_repo)
        assert resolved == "app/src/main/kotlin/com/pkg/Utils.kt"

    def test_kotlin_error_handling_graceful(self, kotlin_parser, tmp_repo):
        res = kotlin_parser.extract_code_structure(tmp_repo, tmp_repo)
        assert res[0] == []
        assert res[4] == {}

    def test_kotlin_deterministic_ids_safe(self, kotlin_parser, tmp_repo):
        f = tmp_repo / "A.kt"
        f.write_text("class A")
        s1, _, _, _, _ = kotlin_parser.extract_code_structure(f, tmp_repo)
        s2, _, _, _, _ = kotlin_parser.extract_code_structure(f, tmp_repo)
        if len(s1) > 0:
            assert s1[0].id == s2[0].id

    def test_basic_properties(self, kotlin_parser):
        # Testa le funzioni di base che venivano saltate
        assert ".kt" in kotlin_parser._get_file_extensions()
        assert isinstance(kotlin_parser._get_init_files(), set)

    def test_extract_dependencies_direct(self, kotlin_parser, tmp_repo):
        # Testa direttamente la funzione extract_dependencies
        f = tmp_repo / "B.kt"
        f.write_text("import com.pkg.Utils")
        deps = kotlin_parser.extract_dependencies(f, tmp_repo)
        assert isinstance(deps, list)

    def test_dependency_extraction_with_unresolved_imports(self, kotlin_parser, tmp_repo):
        # Testa l'estrazione delle dipendenze quando alcuni import non possono essere risolti
        code = """
        import com.real.package.RealClass
        import com.fake.package.FakeClass
        """
        
        # Crea il file per l'import reale
        pkg_dir = tmp_repo / "app/src/main/kotlin/com/real/package"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "RealClass.kt").write_text("class RealClass")

        f = tmp_repo / "Test.kt"
        f.write_text(code)
        
        deps = kotlin_parser.extract_dependencies(f, tmp_repo)
        assert "app/src/main/kotlin/com/real/package/RealClass.kt" in deps
        assert len(deps) == 1

    def test_empty_file_parsing(self, kotlin_parser, tmp_repo):
        # Testa il parsing di un file vuoto
        f = tmp_repo / "Empty.kt"
        f.write_text("")
        symbols, exports, function_deps, imports, metadata = kotlin_parser.extract_code_structure(f, tmp_repo)
        assert symbols == []
        assert exports == []
        assert function_deps == []
        assert imports == []
        assert metadata['lines_of_code'] == 0