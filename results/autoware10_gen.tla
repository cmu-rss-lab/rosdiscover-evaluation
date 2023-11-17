
------------------------------- MODULE autoware10 -------------------------------
EXTENDS Sequences, Integers, TLC, FiniteSets
CONSTANTS Obj_reproj, Image_obj_tracked, Current_pose, Unknown, Data, NULL, MaxQueue

ASSUME NULL \notin Data


\* helper functions
SeqOf(set, n) == UNION {[1..m -> set] : m \in 0..n} \* generates all sequences no longer than n consisting of elements in set
seq (+) elem == Append(seq, elem)

(*--fair algorithm polling
variables
    	image_obj_tracked = <<>>;
	image_obj_tracked_obj_reproj = <<>>;
	current_pose = <<>>;
	current_pose_obj_reproj = <<>>;
	obj_label_marker = <<>>;
	obj_label = <<>>;
	unknown = <<>>;
	unknown_obj_reproj = <<>>;
	obj_label_bounding_box = <<>>;

    define 
        TypeInvariant == 
 	image_obj_tracked \in SeqOf(Data, MaxQueue) /\ 
	image_obj_tracked_obj_reproj \in SeqOf(Data, MaxQueue) /\ 
	current_pose \in SeqOf(Data, MaxQueue) /\ 
	current_pose_obj_reproj \in SeqOf(Data, MaxQueue) /\ 
	obj_label_marker \in SeqOf(Data, MaxQueue) /\ 
	obj_label \in SeqOf(Data, MaxQueue) /\ 
	unknown \in SeqOf(Data, MaxQueue) /\ 
	unknown_obj_reproj \in SeqOf(Data, MaxQueue) /\ 
	obj_label_bounding_box \in SeqOf(Data, MaxQueue)

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
    
    fair process image_obj_tracked \in Image_obj_tracked
        
        begin 
            Write: 
                if image_obj_tracked /= <<>> then
                    msg := Head(image_obj_tracked);
                    image_obj_tracked := Tail(image_obj_tracked);
                        image_obj_tracked_obj_reproj := image_obj_tracked_obj_reproj (+) msg;

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
    
    fair process unknown \in Unknown
        
        begin 
            Write: 
                if unknown /= <<>> then
                    msg := Head(unknown);
                    unknown := Tail(unknown);
                        unknown_obj_reproj := unknown_obj_reproj (+) msg;

                end if;
        end process;
    
end algorithm; *)
====
