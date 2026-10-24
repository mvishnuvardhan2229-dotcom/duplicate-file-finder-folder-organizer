# Test Cases — Input, Expected Result, and Actual Result

**Project:** Duplicate File Finder and Folder Organizer  
**Student:** MACHABATHUNI (VARDHAN) VISHNU VARDHAN  
**Student ID:** O230711

The actual outcomes below are based on the supplied terminal screenshot showing eight automated tests ending with `Ran 8 tests` and `OK`.

![TERMINAL SHOWING TESTS PASSED][/home/rgukt/Desktop/E2 S1/DAA LAB/DAA_Project1_Individual_Submission/docs/screenshots/02_tests.png]


| No. | Test input / action | Expected result | Actual result / evidence |
|---:|---|---|---|
| 1 | Create two files with identical content but different names. | They are detected as duplicates. | Passed in the automated test screenshot: `test_identical_contents_with_different_names ... ok`. |
| 2 | Create two files with different contents. | They are not grouped as duplicates. | Passed in the automated test screenshot: `test_different_contents_not_duplicates ... ok`. |
| 3 | Scan with a file-extension filter, such as `.csv`. | Only files matching the selected extension are included. | Passed in the automated test screenshot: `test_extension_filter ... ok`; the browser screenshot also shows a CSV-filter scan with one eligible file and no duplicate group. |
| 4 | Scan a folder path that does not exist. | The app rejects the path and displays a readable error. | Passed in the automated test screenshot: `test_invalid_folder_rejected ... ok`. |
| 5 | Scan with a minimum-size threshold. | Files below the threshold are excluded. | Passed in the automated test screenshot: `test_minimum_size_filter ... ok`. |
| 6 | Place a file under `_organized` and scan the parent folder. | The app skips its own organized output. | Passed in the automated test screenshot: `test_organized_folder_is_excluded ... ok`. |
| 7 | Build an organization plan for files, including same-named files from different folders. | Preview does not copy files, original files remain, and destination paths are unique. | Passed in the automated test screenshot: `test_plan_preserves_sources_and_unique_destinations ... ok`. |
| 8 | Compute a fingerprint for the same unchanged file more than once. | The fingerprint remains stable. | Passed in the automated test screenshot: `test_fingerprint_is_stable ... ok`. |

