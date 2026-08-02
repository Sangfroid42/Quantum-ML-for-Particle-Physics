! pythia_lhe.cmd
! Pythia 8 configuration to read LHE files

! Process all events in the file (-1 means all)
Main:numberOfEvents = 100000         

! Frame type 4 tells Pythia "read from an LHE file instead of generating events"
Beams:frameType = 4              

! The exact path to your unzipped MadGraph LHE file
Beams:LHEF = /home/edear/FCCAnalyses/darkpho/double_dark/mg5/mg5_background_double_dark/Events/run_01/unweighted_events.lhe
