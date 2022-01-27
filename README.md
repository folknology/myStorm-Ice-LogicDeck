# Ice-LogicDeck 
The very first myStorm [Tile](https://github.com/folknology/Tiles) based logic deck, the design is based around the combination of a powerful STM32 F7 microcontroller fused with a fully configurable Lattice Ice40Hx FPGA.
This forms a modular heterogeneous embedded development system, it is very much WIP, I will add more documentation soon, you can follow the recordings of my [streams](https://www.youtube.com/channel/UCQSPg8L4WFBGuj_MnvQQ7Qw/videos) that narrate it's development and perhaps peruses the [documentation](https://folknology.github.io/myStorm-Ice-LogicDeck/) as we develop it.

##The 'Deck' based solution is formed by combining multiple [Tiles](https://github.com/folknology/Tiles) and the Ice Logic board carrier
![LogicDeck Layout](docs/ILD-Proto-B-UnLoaded.jpg)
## Together these form the Ice LogicDeck solution
![LogicDeck Layout](docs/ILD-Proto-B-Loaded.jpg)

###Hardware, development, tooling and software
- [Hardware sources](https://github.com/folknology/myStorm-Ice-LogicDeck/tree/main/Hardware)
- [Firmware sources](https://github.com/folknology/BlackCrab)
- [Examples & board support](https://github.com/folknology/myStorm-Ice-LogicDeck/tree/main/HDL)
- [Python based HDL - Amaranth](https://github.com/amaranth-lang/amaranth-lang.github.io)
- [FPGA Synthesis, PNR and formal - Yosys](https://github.com/YosysHQ/yosys)
- [Simulation - Verilator](https://github.com/verilator/verilator)

### Further information
- [Tiles](https://github.com/folknology/Tiles)
- [Documentation](https://folknology.github.io/myStorm-Ice-LogicDeck/)
- [Discuss LogicDecks on Discord](https://discord.gg/RCGcgbQNZK)

###OpenSource Design
![LogicDeck Layout](layout.png)
![LogicDeck Schematic](schematic.png)

