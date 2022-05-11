###############################################################################
#                                                                             #
# Copyright 2016 myStorm Copyright and related                                #
# rights are licensed under the Solderpad Hardware License, Version 0.51      #
# (the “License”); you may not use this file except in compliance with        #
# the License. You may obtain a copy of the License at                        #
# http://solderpad.org/licenses/SHL-0.51. Unless required by applicable       #
# law or agreed to in writing, software, hardware and materials               #
# distributed under this License is distributed on an “AS IS” BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or             #
# implied. See the License for the specific language governing                #
# permissions and limitations under the License.                              #
#                                                                             #
###############################################################################



VERILOG = toplevel.v blink.v

bin/toplevel.json : ${VERILOG}
	mkdir -p bin
	yosys -v3 -p "synth_ice40 -top toplevel -json bin/toplevel.json" ${VERILOG}

bin/toplevel.asc : ../IceLogicBus.pcf bin/toplevel.json
	nextpnr-ice40 --freq 64 --hx8k --package bg121:4k --json bin/toplevel.json --pcf ../IceLogicBus.pcf --asc bin/toplevel.asc --opt-timing --placer heap

bin/toplevel.bin : bin/toplevel.asc
	icepack bin/toplevel.asc bin/toplevel.bin

compile : bin/toplevel.bin

time: bin/toplevel.bin
	icetime -tmd hx8k bin/toplevel.asc

prog : bin/toplevel.bin
	stty -F /dev/ttyACM0 raw
	cat bin/toplevel.bin >/dev/ttyACM0

clean :
	rm -rf bin
	$(RM) -f chip.blif chip.txt chip.ex chip.bin
