
------------------------------- MODULE autoware03 -------------------------------
EXTENDS Sequences, Integers, TLC, FiniteSets
CONSTANTS Velocity_set, Localizer_pose, Odom_pose, Control_pose, Base_waypoints, Data, NULL, MaxQueue

ASSUME NULL \notin Data


\* helper functions
SeqOf(set, n) == UNION {[1..m -> set] : m \in 0..n} \* generates all sequences no longer than n consisting of elements in set
seq (+) elem == Append(seq, elem)

(*--fair algorithm polling
variables
    	localizer_pose = <<>>;
	localizer_pose_velocity_set = <<>>;
	detection_range = <<>>;
	odom_pose = <<>>;
	odom_pose_lattice_trajectory_gen = <<>>;
	odom_pose_velocity_set = <<>>;
	closest_waypoint = <<>>;
	cubic_splines_viz = <<>>;
	obstacle = <<>>;
	control_pose = <<>>;
	control_pose_lattice_trajectory_gen = <<>>;
	base_waypoints = <<>>;
	base_waypoints_velocity_set = <<>>;
	base_waypoints_lattice_trajectory_gen = <<>>;
	unknown_topic = <<>>;
	temporal_waypoints = <<>>;

    define 
        TypeInvariant == 
 	localizer_pose \in SeqOf(Data, MaxQueue) /\ 
	localizer_pose_velocity_set \in SeqOf(Data, MaxQueue) /\ 
	detection_range \in SeqOf(Data, MaxQueue) /\ 
	odom_pose \in SeqOf(Data, MaxQueue) /\ 
	odom_pose_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	odom_pose_velocity_set \in SeqOf(Data, MaxQueue) /\ 
	closest_waypoint \in SeqOf(Data, MaxQueue) /\ 
	cubic_splines_viz \in SeqOf(Data, MaxQueue) /\ 
	obstacle \in SeqOf(Data, MaxQueue) /\ 
	control_pose \in SeqOf(Data, MaxQueue) /\ 
	control_pose_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	base_waypoints \in SeqOf(Data, MaxQueue) /\ 
	base_waypoints_velocity_set \in SeqOf(Data, MaxQueue) /\ 
	base_waypoints_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	unknown_topic \in SeqOf(Data, MaxQueue) /\ 
	temporal_waypoints \in SeqOf(Data, MaxQueue)

        Response == <>(closest_waypoint /= <<>>)
    end define;

    fair process velocity_set \in Velocity_set
        variables
		msg \in Data;
		g_path_flag = FALSE;
		g_pose_flag = FALSE;
		false_count = 0;
		prev_detection = -1;

        begin 
            
                10_0Hz:
                    if ((~(g_pose_flag = FALSE)) /\ (~((g_pose_flag = FALSE) \/ (g_path_flag = FALSE)))) then
                        
                        detection_range := detection_range (+) msg;
                        temporal_waypoints := temporal_waypoints (+) msg;
                        closest_waypoint := closest_waypoint (+) msg;
                        obstacle := obstacle (+) msg;

                    end if;
                
            localizer_pose_velocity_set:
                if localizer_pose_velocity_set /= <<>> then
                    msg := Head(localizer_pose_velocity_set);
                    localizer_pose_velocity_set := Tail(localizer_pose_velocity_set);
                    
                            if (g_pose_flag = FALSE) then
                                g_pose_flag := TRUE;

    
                            end if;
                    
                end if;
            
            odom_pose_velocity_set:
                if odom_pose_velocity_set /= <<>> then
                    msg := Head(odom_pose_velocity_set);
                    odom_pose_velocity_set := Tail(odom_pose_velocity_set);
                    
                            if (g_pose_flag = FALSE) then
                                g_pose_flag := TRUE;

    
                            end if;
                    
                end if;
            
            base_waypoints_velocity_set:
                if base_waypoints_velocity_set /= <<>> then
                    msg := Head(base_waypoints_velocity_set);
                    base_waypoints_velocity_set := Tail(base_waypoints_velocity_set);
                    
                            if (g_path_flag = FALSE) then
                                g_path_flag := TRUE;

    
                            end if;
                    
                end if;
            
        end process;
    
    fair process localizer_pose \in Localizer_pose
        
        begin 
            Write: 
                if localizer_pose /= <<>> then
                    msg := Head(localizer_pose);
                    localizer_pose := Tail(localizer_pose);
                        localizer_pose_velocity_set := localizer_pose_velocity_set (+) msg;

                end if;
        end process;
    
    fair process odom_pose \in Odom_pose
        
        begin 
            Write: 
                if odom_pose /= <<>> then
                    msg := Head(odom_pose);
                    odom_pose := Tail(odom_pose);
                        odom_pose_lattice_trajectory_gen := odom_pose_lattice_trajectory_gen (+) msg;
                        odom_pose_velocity_set := odom_pose_velocity_set (+) msg;

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
                        base_waypoints_velocity_set := base_waypoints_velocity_set (+) msg;
                        base_waypoints_lattice_trajectory_gen := base_waypoints_lattice_trajectory_gen (+) msg;

                end if;
        end process;
    
end algorithm; *)
====
