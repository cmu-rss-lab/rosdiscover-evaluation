
------------------------------- MODULE autoware02 -------------------------------
EXTENDS Sequences, Integers, TLC, FiniteSets
CONSTANTS Lattice_trajectory_gen, Odom_pose, Control_pose, Base_waypoints, Data, NULL, MaxQueue

ASSUME NULL \notin Data


\* helper functions
SeqOf(set, n) == UNION {[1..m -> set] : m \in 0..n} \* generates all sequences no longer than n consisting of elements in set
seq (+) elem == Append(seq, elem)

(*--fair algorithm polling
variables
    	odom_pose = <<>>;
	odom_pose_lattice_trajectory_gen = <<>>;
	cubic_splines_viz = <<>>;
	control_pose = <<>>;
	control_pose_lattice_trajectory_gen = <<>>;
	base_waypoints = <<>>;
	base_waypoints_lattice_trajectory_gen = <<>>;
	unknown_topic = <<>>;

    define 
        TypeInvariant == 
 	odom_pose \in SeqOf(Data, MaxQueue) /\ 
	odom_pose_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	cubic_splines_viz \in SeqOf(Data, MaxQueue) /\ 
	control_pose \in SeqOf(Data, MaxQueue) /\ 
	control_pose_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	base_waypoints \in SeqOf(Data, MaxQueue) /\ 
	base_waypoints_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	unknown_topic \in SeqOf(Data, MaxQueue)

        Response == <>(cubic_splines_viz /= <<>>)
    end define;

    fair process lattice_trajectory_gen \in Lattice_trajectory_gen
        variables
		msg \in Data;
		g_waypoint_set = FALSE;
		g_pose_set = FALSE;

        begin 
            
                10_0Hz:
                    if ((~(g_waypoint_set = FALSE)) /\ (~((g_waypoint_set = FALSE) \/ (g_pose_set = FALSE)))) then
                        
                        unknown_topic := unknown_topic (+) msg;
                        cubic_splines_viz := cubic_splines_viz (+) msg;

                    end if;
                
            base_waypoints_lattice_trajectory_gen:
                if base_waypoints_lattice_trajectory_gen /= <<>> then
                    msg := Head(base_waypoints_lattice_trajectory_gen);
                    base_waypoints_lattice_trajectory_gen := Tail(base_waypoints_lattice_trajectory_gen);
                    
                            if TRUE then
                                g_waypoint_set := TRUE;

    
                            end if;
                    
                end if;
            
            control_pose_lattice_trajectory_gen:
                if control_pose_lattice_trajectory_gen /= <<>> then
                    msg := Head(control_pose_lattice_trajectory_gen);
                    control_pose_lattice_trajectory_gen := Tail(control_pose_lattice_trajectory_gen);
                    
                            if TRUE then
                                g_pose_set := TRUE;

    
                            end if;
                    
                end if;
            
            odom_pose_lattice_trajectory_gen:
                if odom_pose_lattice_trajectory_gen /= <<>> then
                    msg := Head(odom_pose_lattice_trajectory_gen);
                    odom_pose_lattice_trajectory_gen := Tail(odom_pose_lattice_trajectory_gen);
                    
                            if g_sim_mode then
                                g_pose_set := TRUE;

    
                            end if;
                    
                end if;
            
        end process;
    
    fair process odom_pose \in Odom_pose
        
        begin 
            Write: 
                if odom_pose /= <<>> then
                    msg := Head(odom_pose);
                    odom_pose := Tail(odom_pose);
                        odom_pose_lattice_trajectory_gen := odom_pose_lattice_trajectory_gen (+) msg;

                end if;
        end process;
    
    fair process control_pose \in Control_pose
        
        begin 
            Write: 
                if control_pose /= <<>> then
                    msg := Head(control_pose);
                    control_pose := Tail(control_pose);
                        control_pose_lattice_trajectory_gen := control_pose_lattice_trajectory_gen (+) msg;

                end if;
        end process;
    
    fair process base_waypoints \in Base_waypoints
        
        begin 
            Write: 
                if base_waypoints /= <<>> then
                    msg := Head(base_waypoints);
                    base_waypoints := Tail(base_waypoints);
                        base_waypoints_lattice_trajectory_gen := base_waypoints_lattice_trajectory_gen (+) msg;

                end if;
        end process;
    
end algorithm; *)
====
