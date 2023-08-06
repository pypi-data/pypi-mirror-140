"""Tests for the writing rules."""
import warnings

import pytest

import provenancetoolbox as ptb
from cirrusvolume import rules


SOURCES = ['A', 'B', 'C']
MOTIVATION = "Trying to improve"
PROCESS = ptb.Process(
              'testing CirrusVolume',
              {'patience for humor': 3/10},
              ptb.PythonGithubEnv('.')
          )


class TestCheckWritingRules:
    """Tests whether rules.check_writing_rules enforces what we want."""

    def test_basic(self):
        """Does the function pass with the expected args."""
        rules.check_writing_rules(SOURCES, MOTIVATION, PROCESS)

    def test_nones(self):
        """Does the function raise an AssertionError with Nones."""
        with pytest.raises(AssertionError):
            rules.check_writing_rules(None, MOTIVATION, PROCESS)
    
        with pytest.raises(AssertionError):
            rules.check_writing_rules(SOURCES, None, PROCESS)
    
        with pytest.raises(AssertionError):
            rules.check_writing_rules(SOURCES, MOTIVATION, None)

    def test_types(self):
        """Does the function raise an AssertionError with incorrect types."""
        # sources not a list of strings
        with pytest.raises(AssertionError):
            rules.check_writing_rules(0, MOTIVATION, PROCESS)
    
        with pytest.raises(AssertionError):
            rules.check_writing_rules([0], MOTIVATION, PROCESS)
    
        # motivation not a string
        with pytest.raises(AssertionError):
            rules.check_writing_rules(SOURCES, 0, PROCESS)
    
        # process not a ptb.Process
        with pytest.raises(AssertionError):
            rules.check_writing_rules(SOURCES, MOTIVATION, 0)


class TestAddSources:
    """Tests for rules.add_sources."""

    def test_new_sources(self, readvolume):
        """Does writing sources to an empty volume work?"""
        rules.add_sources(readvolume, SOURCES)
        newsources = readvolume.provenance.sources

        assert set(newsources) == set(SOURCES)

    def test_intersection(self, readwritevolume):
        """Are duplicate sources written?"""
        sources = readwritevolume.provenance.sources

        rules.add_sources(readwritevolume, sources)

        assert len(sources) == len(readwritevolume.provenance.sources)


class TestAddMotivation:
    """Tests for rules.add_motivation."""

    def test_new_motivation(self, readvolume):
        """Does writing the motivation to an empty volume work?"""
        assert ptb.note_absent(readvolume, MOTIVATION, ptb.NoteType.MOTIVATION)

        rules.add_motivation(readvolume, MOTIVATION)

        assert not ptb.note_absent(
                       readvolume, MOTIVATION, ptb.NoteType.MOTIVATION)

    def test_intersection(self, readwritevolume):
        """Are duplicate motivations written?"""
        assert ptb.note_absent(
                   readwritevolume, MOTIVATION, ptb.NoteType.MOTIVATION
               )

        num_orig_notes = len(ptb.parsenotes(readwritevolume))
        rules.add_motivation(readwritevolume, MOTIVATION)
        num_new_notes = len(ptb.parsenotes(readwritevolume))

        assert num_new_notes == num_orig_notes + 1

        rules.add_motivation(readwritevolume, MOTIVATION)
        num_newer_notes = len(ptb.parsenotes(readwritevolume))

        assert num_newer_notes == num_new_notes


class TestAddProcess:
    """Tests for rules.add_process."""

    def test_new_process(self, readvolume):
        """Does writing the motivation to an empty volume work?"""
        assert ptb.process_absent(readvolume, PROCESS)

        rules.add_process(readvolume, PROCESS)

        assert not ptb.process_absent(readvolume, PROCESS)

    def test_intersection(self, readwritevolume):
        """Are duplicate processes written?"""
        assert ptb.process_absent(readwritevolume, PROCESS)

        num_orig_procs = len(readwritevolume.provenance.processing)
        rules.add_process(readwritevolume, PROCESS)
        num_new_procs = len(readwritevolume.provenance.processing)

        assert num_new_procs == num_orig_procs + 1

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            rules.add_process(readwritevolume, PROCESS)
        num_newer_procs = len(readwritevolume.provenance.processing)

        assert num_newer_procs == num_new_procs

