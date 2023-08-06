@rem
@rem pagemarks - Free, git-backed, self-hosted bookmarks
@rem Copyright (c) 2019-2021 the pagemarks contributors
@rem
@rem This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
@rem License, version 3, as published by the Free Software Foundation.
@rem This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
@rem warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
@rem details.
@rem You should have received a copy of the GNU General Public License along with this program.
@rem If not, see https://www.gnu.org/licenses/gpl.html.
@rem __________________________________________________________________________________________________________________
@rem
@rem Transfer the demo_repo from its original folder to a git repo under build/
set PAGEMARKS_REPO=build\demo_repo
if not exist %PAGEMARKS_REPO% mkdir %PAGEMARKS_REPO%
if not exist %PAGEMARKS_REPO%\.git (
    git -C %PAGEMARKS_REPO% init
    git -C %PAGEMARKS_REPO% config --local commit.gpgsign false
)
xcopy /i /q /s /y demo_repo %PAGEMARKS_REPO%
git -C %PAGEMARKS_REPO% add *
git -C %PAGEMARKS_REPO% commit -m "Transfer demo_repo data"
@rem
@rem Extend PATH
set PATH=_support\bin;node_modules\.bin;%PATH%
@rem
@rem Show reminder for author if present
if exist _support\bin\remind.bat call _support\bin\remind.bat
@rem
@rem Activate the Python virtual environment (venv)
venv\Scripts\activate.bat
