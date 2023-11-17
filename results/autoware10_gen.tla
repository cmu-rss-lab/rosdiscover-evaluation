
------------------------------- MODULE autoware10 -------------------------------
EXTENDS Sequences, Integers, TLC, FiniteSets
CONSTANTS Obj_reproj, Localizer_pose, Image_obj_tracked, Odom_pose, Unknown, Control_pose, Current_pose, Base_waypoints, Data, NULL, MaxQueue

ASSUME NULL \notin Data


\* helper functions
SeqOf(set, n) == UNION {[1..m -> set] : m \in 0..n} \* generates all sequences no longer than n consisting of elements in set
seq (+) elem == Append(seq, elem)

(*--fair algorithm polling
variables
    	localizer_pose = <<>>;
	localizer_pose_velocity_set = <<>>;
	obj_label_marker = <<>>;
	image_obj_tracked = <<>>;
	image_obj_tracked_obj_reproj = <<>>;
	obj_label_bounding_box = <<>>;
	obj_label = <<>>;
	detection_range = <<>>;
	odom_pose = <<>>;
	odom_pose_lattice_trajectory_gen = <<>>;
	odom_pose_velocity_set = <<>>;
	closest_waypoint = <<>>;
	cubic_splines_viz = <<>>;
	obstacle = <<>>;
	unknown = <<>>;
	unknown_obj_reproj = <<>>;
	control_pose = <<>>;
	control_pose_lattice_trajectory_gen = <<>>;
	current_pose = <<>>;
	current_pose_obj_reproj = <<>>;
	base_waypoints = <<>>;
	base_waypoints_velocity_set = <<>>;
	base_waypoints_lattice_trajectory_gen = <<>>;
	unknown_topic = <<>>;
	temporal_waypoints = <<>>;

    define 
        TypeInvariant == 
 	localizer_pose \in SeqOf(Data, MaxQueue) /\ 
	localizer_pose_velocity_set \in SeqOf(Data, MaxQueue) /\ 
	obj_label_marker \in SeqOf(Data, MaxQueue) /\ 
	image_obj_tracked \in SeqOf(Data, MaxQueue) /\ 
	image_obj_tracked_obj_reproj \in SeqOf(Data, MaxQueue) /\ 
	obj_label_bounding_box \in SeqOf(Data, MaxQueue) /\ 
	obj_label \in SeqOf(Data, MaxQueue) /\ 
	detection_range \in SeqOf(Data, MaxQueue) /\ 
	odom_pose \in SeqOf(Data, MaxQueue) /\ 
	odom_pose_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	odom_pose_velocity_set \in SeqOf(Data, MaxQueue) /\ 
	closest_waypoint \in SeqOf(Data, MaxQueue) /\ 
	cubic_splines_viz \in SeqOf(Data, MaxQueue) /\ 
	obstacle \in SeqOf(Data, MaxQueue) /\ 
	unknown \in SeqOf(Data, MaxQueue) /\ 
	unknown_obj_reproj \in SeqOf(Data, MaxQueue) /\ 
	control_pose \in SeqOf(Data, MaxQueue) /\ 
	control_pose_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	current_pose \in SeqOf(Data, MaxQueue) /\ 
	current_pose_obj_reproj \in SeqOf(Data, MaxQueue) /\ 
	base_waypoints \in SeqOf(Data, MaxQueue) /\ 
	base_waypoints_velocity_set \in SeqOf(Data, MaxQueue) /\ 
	base_waypoints_lattice_trajectory_gen \in SeqOf(Data, MaxQueue) /\ 
	unknown_topic \in SeqOf(Data, MaxQueue) /\ 
	temporal_waypoints \in SeqOf(Data, MaxQueue)

        Response == <>(obj_label_marker /= <<>>)
    end define;

    fair process obj_reproj \in Obj_reproj
        variables
		msg \in Data;
		isReady_ndt_pose = FALSE;
		isReady_obj_pos_xyz = FALSE;
		ready_ = FALSE;

        begin 
            
            image_obj_tracked_obj_reproj:
                if image_obj_tracked_obj_reproj /= <<>> then
                    msg := Head(image_obj_tracked_obj_reproj);
                    image_obj_tracked_obj_reproj := Tail(image_obj_tracked_obj_reproj);
                    obj_label := obj_label (+) msg;
obj_label_marker := obj_label_marker (+) msg;
obj_label_bounding_box := obj_label_bounding_box (+) msg;

                            if ((ready_ /\ isReady_obj_pos_xyz) /\ (isReady_obj_pos_xyz /\ isReady_ndt_pose)) then
                                isReady_ndt_pose := FALSE;
                            isReady_obj_pos_xyz := FALSE;

    
                            elsif ready_ then
                                isReady_obj_pos_xyz := TRUE;

    
                            end if;
                    
                end if;
            
            current_pose_obj_reproj:
                if current_pose_obj_reproj /= <<>> then
                    msg := Head(current_pose_obj_reproj);
                    current_pose_obj_reproj := Tail(current_pose_obj_reproj);
                    obj_label := obj_label (+) msg;
obj_label_marker := obj_label_marker (+) msg;
obj_label_bounding_box := obj_label_bounding_box (+) msg;

                            if (isReady_obj_pos_xyz /\ (isReady_obj_pos_xyz /\ isReady_ndt_pose)) then
                                isReady_obj_pos_xyz := FALSE;
                            isReady_ndt_pose := FALSE;

    
                            elsif TRUE then
                                isReady_ndt_pose := TRUE;

    
                            end if;
                    
                end if;
            
            unknown_obj_reproj:
                if unknown_obj_reproj /= <<>> then
                    msg := Head(unknown_obj_reproj);
                    unknown_obj_reproj := Tail(unknown_obj_reproj);
                    
                            if TRUE then
                                ready_ := TRUE;

    
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
    
    fair process image_obj_tracked \in Image_obj_tracked
        
        begin 
            Write: 
                if image_obj_tracked /= <<>> then
                    msg := Head(image_obj_tracked);
                    image_obj_tracked := Tail(image_obj_tracked);
                        image_obj_tracked_obj_reproj := image_obj_tracked_obj_reproj (+) msg;

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
    
    fair process unknown \in Unknown
        
        begin 
            Write: 
                if unknown /= <<>> then
                    msg := Head(unknown);
                    unknown := Tail(unknown);
                        unknown_obj_reproj := unknown_obj_reproj (+) msg;

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
    
    fair process current_pose \in Current_pose
        
        begin 
            Write: 
                if current_pose /= <<>> then
                    msg := Head(current_pose);
                    current_pose := Tail(current_pose);
                        current_pose_obj_reproj := current_pose_obj_reproj (+) msg;

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
