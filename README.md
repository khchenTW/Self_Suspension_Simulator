The file stucture:
- simulator.py: the kernel of the simulator. You can find that how the events are created and what's the concepts in inside.
- task_generator.py: the UUnifast task generator. The period now is in range [1-100] (the value is rounded)
- TDA.py: several TDA routines. It is used for prechecking the generated task set. There are two type of tests: One for all tasks, and another one for only hard tasks.
- experiments.py: experimental routines - mode 0 generate task set to input folder with numpy / mode 1 execute the simulation.
- sort_task_set.py: two simple routines for sorting based on the chosen criteria
- mixed_task_builder.py: based on the original task set to generate mixed task set

Three events definitions:
- Release event: A \texttt{release} event of $\tau_i$ adds its initial workload, i.e., either $c_{i,1}+p_i$ or $c_{i,1}$, to the entry of $\tau_i$ in the status table depending on the system mode, and places a \texttt{deadline} event and a \texttt{suspension} event of $\tau_i$ into the event list. 
- Deadline event: A \texttt{deadline} event of the lowest priority task in $\Gamma_{hard}$ will determine if it is the point in time $\zeta$ to initialize the second transient phase. 
- Suspension event: A \texttt{suspension} event of $\tau_i$ adds its remaining workload, either $q_i + c_{i,2}$ executing in the normal mode or $c_{i,s} + c_{i,2}$ in the safe mode. There is one more task mode (defined as 2), which is a legacy of mode change. It means that there was a suspension event of this task before in the current period.
