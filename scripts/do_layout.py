import re
import sys
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-r', '--reference', help="reference file")
parser.add_argument('-f', '--file', help="file to apply layout to")

args = parser.parse_args()

ref_filename = args.reference
app_filename = args.file

ref_header_regex = r"MX_Alps_Hybrid:MX-([0-9\.]+)U"
out_header_regex = r"footprint \"MX_Only:MX_Lekker"
led_header_regex = r"footprint \"random-keyboard-parts:QBLP677R-RGB"
hall_header_regex = r"footprint \"random_parts:SOT-23_Handsoldering_no_plane\""
cap_header_regex = r"footprint \"Capacitor_SMD:C_0603_1608Metric_Pad1.08x0.95mm_HandSolder"
at_regex = r"\(at ([0-9\.]+) ([0-9\.]+)"
key_regex = r"(K_[0-9]+)"
lekker_regex = r"(SW[0-9]+)"
led_regex = r"(S[0-9]+)"
hall_regex = r"(U[0-9]+)"
cap_regex = r"(C[0-9]+)"

# generate dictionary of names
position_dict = {}
with open(ref_filename, "r") as ref_file:
    state = 0
    position = (None,None)
    for line in ref_file:
        # find the header
        if state == 0:
            headers = re.search(ref_header_regex, line)
            if (headers is not None):
                state = 1

        # find the at line
        elif state == 1:
            pos_search = re.search(at_regex, line)
            if pos_search is not None and pos_search.group(1) is not None and pos_search.group(2) is not None:
                position = (float(pos_search.group(1)), float(pos_search.group(2)))
                state = 2

        # find the key
        elif state == 2:
            key_search = re.search(key_regex, line)
            if key_search is not None and key_search.group(1) is not None:
                position_dict[key_search.group(1)] = position

                # reset machine
                position = (None, None)
                state = 0

print(position_dict)

# find the lines where the changes need to go
key_line_dict = {}
led_line_dict = {}
hall_line_dict = {}
cap_line_dict = {}
with open(app_filename) as app_file:
    lines = app_file.readlines()
    test = False
    # find all the lines for every key
    state = 0
    state1 = 0
    state2 = 0
    state3 = 0
    save_line = None
    save_line1 = None
    save_line2 = None
    save_line3 = None
    for (line_num, line) in enumerate(lines):
        # print(line)
        # find the header
        if state == 0:
            headers = re.search(out_header_regex, line)
            if headers is not None or "mini-general-tweaks:RotaryEncoder_Alps_EC11E-Switch-Vertical-EDIT" in line:
                if ("mini-general-tweaks:RotaryEncoder_Alps_EC11E-Switch-Vertical-EDIT" in line):
                    print("asdfa")
                state = 1

        # find the at line
        elif state == 1:
            pos_search = re.search(at_regex, line)
            if pos_search is not None and pos_search.group(1) is not None and pos_search.group(2) is not None:
                save_line = line_num
                if test: print(line); test = False
                state = 2

        # find the key
        elif state == 2:
            key_search = re.search(lekker_regex, line)
            if key_search is not None and key_search.group(1) is not None:
                key_line_dict[key_search.group(1)] = save_line
                
                # reset machine
                save_line = None
                state = 0

        ########### For LEDS
        # find the header
        if state1 == 0:
            headers = re.search(led_header_regex, line)
            if (headers is not None):
                state1 = 1

        # find the at line
        elif state1 == 1:
            pos_search = re.search(at_regex, line)
            if pos_search is not None and pos_search.group(1) is not None and pos_search.group(2) is not None:
                save_line1 = line_num
                state1 = 2

        # find the key
        elif state1 == 2:
            key_search = re.search(led_regex, line)
            if key_search is not None and key_search.group(1) is not None:
                led_line_dict[key_search.group(1)] = save_line1
                # reset machine
                save_line1 = None
                state1 = 0

        ########### For Hall Sensors
        # find the header
        if state2 == 0:
            headers = re.search(hall_header_regex, line)
            if (headers is not None):
                state2 = 1

        # find the at line
        elif state2 == 1:
            pos_search = re.search(at_regex, line)
            if pos_search is not None and pos_search.group(1) is not None and pos_search.group(2) is not None:
                save_line2 = line_num
                state2 = 2

        # find the key
        elif state2 == 2:
            key_search = re.search(hall_regex, line)
            if key_search is not None and key_search.group(1) is not None:
                hall_line_dict[key_search.group(1)] = save_line2
                # reset machine
                save_line2 = None
                state2 = 0

        ########### For Capacitors
        # find the header
        if state3 == 0:
            headers = re.search(cap_header_regex, line)
            if (headers is not None):
                state3 = 1

        # find the at line
        elif state3 == 1:
            pos_search = re.search(at_regex, line)
            if pos_search is not None and pos_search.group(1) is not None and pos_search.group(2) is not None:
                save_line3 = line_num
                state3 = 2

        # find the key
        elif state3 == 2:
            key_search = re.search(cap_regex, line)
            if key_search is not None and key_search.group(1) is not None:
                cap_line_dict[key_search.group(1)] = save_line3
                # reset machine
                save_line3 = None
                state3 = 0



    print("\n") 
    print(key_line_dict)
    print(led_line_dict)
    print(hall_line_dict)

# Apply changes
with open(app_filename, "w") as app_file:
    # apply change to every line
    for key in key_line_dict:
        # layout reference uses zero indexing. I didn't.
        lekker_key_number = int(re.search(r"([0-9]+)", key).group(1))
        lekker_key = "K_"+str(lekker_key_number-1)
        position = position_dict[lekker_key]
        
        lines[key_line_dict[key]] = "    (at %.4f %.4f)\n" % (position[0], position[1])
        hall_key = key.replace("SW", "U")
        lines[hall_line_dict[hall_key]] = "    (at %.4f %.4f 90)\n" % (position[0], position[1])
        # Write the no fill area
        lines[hall_line_dict[hall_key]+45] = "          (xy %.3f %.3f)\n" % (position[0]-1.58, position[1]-1.16)
        lines[hall_line_dict[hall_key]+46] = "          (xy %.3f %.3f)\n" % (position[0]-1.58, position[1]+1.16)
        lines[hall_line_dict[hall_key]+47] = "          (xy %.3f %.3f)\n" % (position[0]+1.58, position[1]+1.16)
        lines[hall_line_dict[hall_key]+48] = "          (xy %.3f %.3f)\n" % (position[0]+1.58, position[1]-1.16)

        # capactiros
        cap_key = key.replace("SW", "C")
        lines[cap_line_dict[cap_key]] = "    (at %.4f %.4f 90)\n" % (position[0]+2.75, position[1])

        if(key != "K_14"):
            led_key = key.replace("SW", "S")
            lines[led_line_dict[led_key]] = "    (at %.4f %.4f)\n" % (position[0], position[1]-5.5)


    app_file.writelines(lines)

# {'D_21': 8241, 'D_56': 492, 'D_50': 577, 'D_0': 577, 'D_57': 1752, 'D_40': 5609, 'D_58': 2523, 'D_23': 10840, 'D_3': 3350, 'D_43': 3350, 'D_10': 4011, 'D_38': 5307, 'D_31': 5609, 'D_36': 4410, 'D_37': 8518, 'D_32': 7649, 'D_25': 4905, 'D_12': 5008, 'D_20': 5442, 'D_63': 5609, 'D_8': 5609, 'D_33': 10935, 'D_19': 6585, 'D_47': 10935, 'D_64': 7313, 'D_49': 7482, 'D_34': 8053, 'D_51': 8688, 'D_14': 9470, 'D_22': 9470, 'D_44': 9470, 'D_54': 10433, 'D_7': 10935, 'D_66': 11634}



# key_move = ["K_65", "K_66", "K_67"]
# for key in key_move:
#     print("%s: %.4f %.4f" % (key, position_dict[key][0], position_dict[key][0]))