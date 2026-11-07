import tkinter as tk
from random import shuffle

import A_star_algo
import BFS_algo
import DFS_algo

global n, solution_branch, solution_steps, total_explored_nodes, execution_time

def shuffle_puzzle():
    global default_input
    L = list(i for j in default_input for i in j)
    shuffle(L)
    default_input= [[L[0],L[1],L[2]],[L[3],L[4],L[5]],[L[6],L[7],L[8]]]
    for i in range(9) :
        ListeT = list(i for j in default_input for i in j)
        ligne, col = i // 3, i % 3
        can.create_image(30 + 110 * col, 30 + 110 * ligne, anchor=tk.NW, image=img[ListeT[i]])

def next_node():
    global n
    n+=1

    for i in range(9) :
        if n>solution_steps:
            break
        else:
            ListeT = list(i for j in solution_branch[n]['taquin'] for i in j)
            ligne, col = i // 3, i % 3
            if n==solution_steps:
                texte.delete("1.0", tk.END)
                texte.insert(tk.END,"END! Here is the last node {}/{} GOAL (You can find the details\nin the file {}_OutPut.txt)".format(n+1, solution_steps+1,algorith))
                texte['fg']='green'
                texte.pack()
            else:
                texte.delete("1.0", tk.END)
                texte.insert(tk.END,"Below is node {}/{} of the solution path".format(n+1, solution_steps+1))
                texte.pack()
            can2.create_image(30 + 110 * col, 30 + 110 * ligne, anchor=tk.NW, image=img[ListeT[i]])
def DFS():
    solve('DFS')
def BFS():
    solve('BFS')
def A_star():
    solve('A_star')

def solve(algo):
    global solution_branch, solution_steps, img, can2, texte, n, total_explored_nodes,algorith
    n=0
    algorith=algo
    if algo=='A_star':
        solution_branch, total_explored_nodes, execution_time = A_star_algo.main(default_input)
    elif algo=='BFS':
        solution_branch, total_explored_nodes, execution_time = BFS_algo.main(default_input)
    elif algo=='DFS':
        solution_branch,total_explored_nodes, execution_time=DFS_algo.main(default_input)


    solution_steps = len(solution_branch) - 1

 
    print("solution-path to GOAL: is found in a .txt file created after this execution && you can traverse this path in the graphical interface")
    print("cost of solution path (steps): {}".format(solution_steps))
    print("total explored/developed nodes at end of execution: {} nodes +1 initial-node".format(total_explored_nodes-1))
    print("execution time: {}".format(execution_time))
    

    
    file = open(algo+'_OutPut.txt', 'a')
    file.write("Solution-path: input-> "+str(solution_branch)+" <-GOAL\n\n")
    file.write("cost of solution path (steps): "+str(solution_steps)+"\n")
    file.write("total explored/developed nodes at end of execution: "+str(total_explored_nodes)+"\n")
    file.write("execution time: "+execution_time+"\n\n")
    file.write("++++++++++++++++++"+"\n\n")
    file.close()
    

    
    mainWindow.destroy()
    
    AstarWindow = tk.Tk()
    AstarWindow['bg'] = 'white'
    AstarWindow.title('AI - Algorithm {}'.format(algo))
    AstarWindow.geometry("520x560-400-150")

    can2 = tk.Canvas(height=380, width=380, bg='ghost white')
    can2.pack(side=tk.BOTTOM)
    can2.pack()

    img = []
    for i in range(9) :
        img.append(tk.PhotoImage(file="img/" + str(i) + ".png"))

    tk.Label(text="Total explored nodes at end of execution: {} nodes +1 initial-node\nCost of solution path (steps): {}\nExecution time: {}".format(
                     total_explored_nodes-1,solution_steps, execution_time),bg='white',width=70,height=5,font=("Arial",10,"bold")).pack()

    texte=tk.Text(font=("Arial", 10,"bold"),fg='black',bg='white',border=1,padx=10,width=60,height=3)
    texte.insert(tk.END, "Below is the initial node.\nTraverse the solution path by clicking the button\n'Next Node' (it can also be found in the file {}_OutPut.txt)".format(algo))
    texte.pack()
    tk.Button(text='Next Node', font=("Arial", 11), fg='black',bg='ghost white', relief=tk.RAISED,
              command=next_node).pack()

    for i in range(9) :
        ListeT = list(i for j in solution_branch[0]['taquin'] for i in j)
        ligne, col = i // 3, i % 3
        can2.create_image(30 + 110 * col, 30 + 110 * ligne, anchor=tk.NW, image=img[ListeT[i]])

    AstarWindow.mainloop()
    

mainWindow = tk.Tk()
mainWindow['bg']= 'white'
mainWindow.title ('AI - Sliding Puzzle Game')
mainWindow.geometry("440x500-400-150")
tk.Label(text="Choose an algorithm to solve in the menu above.\nYou can also shuffle the puzzle.",bg='white',width=50,height=5,font=("Arial",10,"bold")).pack(side=tk.TOP)

can=tk.Canvas(height=380, width=380, bg='ghost white')
can.pack(side =tk.TOP)

img=[]
for i in range(9):
        img.append(tk.PhotoImage(file="img/"+str(i)+".png"))


default_input = [[1, 2, 3],
                [8, 6, 0],
                [7, 5, 4]]



for i in range(9) :
    ListeT = list(i for j in default_input for i in j)
    ligne, col = i // 3, i % 3
    afficher = can.create_image(30 + 110 * col, 30 + 110 * ligne, anchor=tk.NW, image=img[ListeT[i]])

menu = tk.Menu(mainWindow)
menu.add_command(label="Shuffle", command=shuffle_puzzle)
menu.add_command(label="Solve DFS", command=DFS)
menu.add_command(label="Solve BFS", command=BFS)
menu.add_command(label="Solve A*", command=A_star)
mainWindow.config(menu=menu)

mainWindow.mainloop()