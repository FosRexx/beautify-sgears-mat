# beautify-sgears-mat

A tool to convert the popular Minecraft mod [Silent Gear](https://www.curseforge.com/minecraft/mc-mods/silent-gear)'s 
materials TSV dump into an easy-to-read, well-formatted spreadsheet.

## Usage

Before using this tool, you need to first obtain a materials dump from the game. This is necessary because there 
isn’t a straightforward way to view all available materials within the mod. The current solution is to 
use the `/sgear_mats dump` command. You can learn more about this command in the [Silent Gear wiki](https://github.com/SilentChaos512/Silent-Gear/wiki/Starter-Guide#what-materials-are-available).

> ### What Materials Are Available?
>
> This question cannot be properly answered in a wiki, considering the data-driven nature of the mod. Other mods, data packs, and mod packs can all add or modify materials.
> Currently there is no in-game guide book. I will work on it... eventually. It's a difficult task from the coding side.
> 
> #### Spreadsheet Dump Command
> The best solution right now is the use the `/sgear_mats dump` command. This should be done on a singleplayer world with cheats enabled. The resulting TSV file can be imported into any spreadsheet program (Google Sheets, LibreOffice Calc, Excel, etc.) Clicking the path of the file in chat will attempt to open it.

## Steps to use beautify-sgears-mat
### 1. Getting the materials TSV dump
Create a singleplayer world with cheats enabled. Type `/sgear_mats dump` in chat and press Enter. 
This generates a material_export.tsv file, which you can then provide to this program.

### 2. Clone this repo
``` bash
git clone https://github.com/FosRexx/beautify-sgears-mat
cd beautify-sgears-mat
```

### 3. Setting up python virtual environment
#### 3.1 Create a new virtual environment
``` bash
python3 -m venv .venv
```

#### 3.2 Activate the python venv
* Linux:
  ``` bash
  $ source .venv/bin/activate
  ```
* Windows
  ``` cmd
  # cmd.exe
  C:\> .venv\Scripts\activate.bat
  
  # PowerShell
  PS C:\> .venv\Scripts\Activate.ps1
  ```

### 4. Install required dependencies
``` bash
python -m pip install -r requirements.txt
```

### 5. Configuration
Since other mods, data packs, and mod packs can alter materials, their traits, and stats, you may need to 
adjust the configuration to match your Silent Gear version. Modify the `config.json` file in the root directory 
for this purpose. The default configuration is set for the All the Mods 9 mod pack (v0.3.2), the version used 
when developing this tool.

The script generates four spreadsheet sheets: "General," "Tools," "Weapons," and "Armors." The `config.json`
file is structured accordingly. For each sheet, specify:

* Headers: Represent the [Stats](https://github.com/SilentChaos512/Silent-Gear/wiki/Stats) of each material plus
  additional information such as traits, part types, and tier.
* Types: Represents the [Parts Type](https://github.com/SilentChaos512/Silent-Gear/wiki/Parts) for each sheet,
  as not all stats and part types are relevant to every gear category (e.g., "Armor Durability" is irrelevant for tools,
  and an armor cannot use a Cord part).



### 6. Run the tool
``` bash
python beautify-sgears-mat.py --input path/to/tsv/dump
```

