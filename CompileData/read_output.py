from compiling_tools import money_range,print_both

with open("output.txt","r") as file:
    lst=file.readlines()

week_ones=[]
FIXED_MIN_PROFIT=90
weekly_stake=10
total_stake=0
profit=0
weekly_pot_profit=weekly_stake*5
for line in lst:
    if line[15:] == "in week 1\n":
        # print(line)
        week_ones.append(line)
        outcome=int(line[13])
        print_both(outcome)
        total_stake+=weekly_stake*9
        profit+=outcome*weekly_pot_profit
        print_both(profit,total_stake)
        if profit > total_stake:
            print_both(f"This SEASON Profit ={profit - total_stake}")
            total_stake=0
            profit=0
            weekly_stake=10
            weekly_pot_profit=weekly_stake*4.5
            
        else:
            loss=total_stake - profit
            print_both(f"loss{total_stake,profit} =={loss}. loss_range={money_range(amount=loss)}")
            weekly_stake=((loss+FIXED_MIN_PROFIT)/6) 
            weekly_pot_profit=weekly_stake*5
    

print(len(week_ones))