@echo off
git archive --format=zip -o ./data/Reversi-based_RL.zip HEAD
echo Successfully generated zip for botzone!
echo Press any key to continue.
pause
explorer .\data