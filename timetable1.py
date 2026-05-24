import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from collections import defaultdict
import random

class TimetableCSP:
    def __init__(self, courses, teachers, rooms, days, slots_per_day, use_ac3=False, use_mrv=True, use_degree=False, use_lcv=False):
        self.courses = []
        self.course_data = {}  # To store original course information
        
        # Process courses to handle TP teacher options
        for idx, course in enumerate(courses):
            course_name, course_type, teacher_options = course
            # Create a unique identifier for each course
            course_id = f"{course_name}_{course_type}_{idx}"
            self.courses.append(course_id)
            self.course_data[course_id] = {
                'name': course_name,
                'type': course_type,
                'teacher_options': teacher_options,
                'assigned_teacher': None
            }
        
        self.teachers = teachers
        self.rooms = rooms
        self.days = days
        self.slots_per_day = slots_per_day
        self.use_ac3 = use_ac3
        self.use_mrv = use_mrv
        self.use_degree = use_degree
        self.use_lcv = use_lcv
        
        # Generate all possible timeslots
        self.timeslots = []
        for day in days:
            for slot in range(1, slots_per_day[day] + 1):
                self.timeslots.append((day, slot))
        
        # Initialize domains for each course
        self.domains = {}
        for course_id in self.courses:
            course_info = self.course_data[course_id]
            teacher_options = course_info['teacher_options']
            
            # For TP courses, select one teacher from options
            if isinstance(teacher_options, list):
                teacher = random.choice(teacher_options)
                self.course_data[course_id]['assigned_teacher'] = teacher
            else:
                teacher = teacher_options
            
            # Course can be scheduled in any room at any timeslot
            self.domains[course_id] = [(teacher, room, timeslot) for room in rooms for timeslot in self.timeslots]
        
        # Apply AC3 preprocessing if enabled
        if use_ac3:
            self.ac3()
    
    def get_teacher_workdays(self, assignment):
        teacher_days = defaultdict(set)
        for course_id, value in assignment.items():
            teacher, _, (day, _) = value
            teacher_days[teacher].add(day)
        return {teacher: len(days) for teacher, days in teacher_days.items()}
    
    def get_successive_slots(self, assignment, day):
        day_slots = []
        for course_id, value in assignment.items():
            _, _, (slot_day, slot) = value
            if slot_day == day:
                day_slots.append(slot)
        
        day_slots.sort()
        max_successive = 1
        current_successive = 1
        
        for i in range(1, len(day_slots)):
            if day_slots[i] == day_slots[i-1] + 1:
                current_successive += 1
                max_successive = max(max_successive, current_successive)
            else:
                current_successive = 1
        
        return max_successive if day_slots else 0
    
    def is_valid(self, assignment, course_id, value):
        course_info = self.course_data[course_id]
        teacher, room, (day, slot) = value
        
        # # Check for teacher, room, and course conflicts
        # for assigned_course_id, assigned_value in assignment.items():
        #     assigned_info = self.course_data[assigned_course_id]
        #     assigned_teacher, assigned_room, assigned_timeslot = assigned_value
            
        #     # Same timeslot checks
        #     if assigned_timeslot == (day, slot):
        #         if assigned_teacher == teacher:  # Teacher conflict
        #             return False
        #         if assigned_room == room:  # Room conflict
        #             return False
        #         if assigned_info['name'] == course_info['name']:  # Same course conflict
        #             return False
        
        # # Check max 3 successive slots constraint
        # temp_assignment = assignment.copy()
        # temp_assignment[course_id] = value
        # if self.get_successive_slots(temp_assignment, day) > 3:
        #     return False
            
        # return True
        def is_valid(self, assignment, course_id, value):
            course_info = self.course_data[course_id]
            teacher, room, (day, slot) = value
    
    # Check for teacher, room, and course conflicts
            for assigned_course_id, assigned_value in assignment.items():
                assigned_info = self.course_data[assigned_course_id]
                assigned_teacher, assigned_room, assigned_timeslot = assigned_value
        
        # Same timeslot checks
            if assigned_timeslot == (day, slot):
            # No teacher should have more than one course in same slot
                if assigned_teacher == teacher:
                    return False
                # No room should be double-booked
                if assigned_room == room:
                    return False
            # No same course in same slot
                if assigned_info['name'] == course_info['name']:
                    return False
    
    # Check max 3 successive slots constraint
        temp_assignment = assignment.copy()
        temp_assignment[course_id] = value
        if self.get_successive_slots(temp_assignment, day) > 3:
            return False
        
        return True
    def ac3(self):
        queue = [(xi, xj) for xi in self.courses for xj in self.courses if xi != xj]
        while queue:
            xi, xj = queue.pop(0)
            if self.revise(xi, xj):
                if not self.domains[xi]:
                    return False
                for xk in self.courses:
                    if xk != xi and (xk, xi) not in queue:
                        queue.append((xk, xi))
        return True
    
    def revise(self, xi, xj):
        revised = False
        for x in list(self.domains[xi]):
            if not any(self.is_consistent(xi, x, xj, y) for y in self.domains[xj]):
                self.domains[xi].remove(x)
                revised = True
        return revised
    
    def is_consistent(self, xi, x, xj, y):
        if xi == xj:
            return True
        
        _, _, (day_x, slot_x) = x
        _, _, (day_y, slot_y) = y
        
        if (day_x, slot_x) == (day_y, slot_y):
            if x[0] == y[0] or x[1] == y[1]:  # Teacher or room conflict
                return False
        return True
    
    def order_domain_values(self, course_id, assignment):
        domain = list(self.domains[course_id])
        if self.use_lcv:
            def count_constraints(value):
                count = 0
                for other_course_id in self.courses:
                    if other_course_id not in assignment:
                        for val in self.domains[other_course_id]:
                            if not self.is_consistent(course_id, value, other_course_id, val):
                                count += 1
                return count
            domain.sort(key=count_constraints)
        return domain
    
    def select_unassigned_variable(self, assignment):
        unassigned = [c for c in self.courses if c not in assignment]
        if not unassigned:
            return None
        
        if self.use_mrv:
            return min(unassigned, key=lambda c: len(self.domains[c]))
        
        if self.use_degree:
            def degree(c):
                count = 0
                for other in unassigned:
                    if other != c:
                        for v in self.domains[c]:
                            for ov in self.domains[other]:
                                if not self.is_consistent(c, v, other, ov):
                                    count += 1
                return count
            return max(unassigned, key=degree)
        
        return unassigned[0]
    
    def forward_check(self, assignment, course_id, value):
        saved_domains = {c: list(self.domains[c]) for c in self.courses if c not in assignment}
        
        for other_course_id in self.courses:
            if other_course_id not in assignment:
                self.domains[other_course_id] = [
                    val for val in self.domains[other_course_id]
                    if self.is_consistent(other_course_id, val, course_id, value)
                ]
                if not self.domains[other_course_id]:
                    # Restore domains and return failure
                    for c, domain in saved_domains.items():
                        self.domains[c] = domain
                    return False
        return True
    
    def backtrack(self, assignment=None):
        if assignment is None:
            assignment = {}
        
        if len(assignment) == len(self.courses):
            # Check soft constraint violations
            teacher_workdays = self.get_teacher_workdays(assignment)
            violations = sum(1 for days in teacher_workdays.values() if days > 2)
            return assignment, violations
        
        var = self.select_unassigned_variable(assignment)
        if var is None:
            return None, 0
        
        for value in self.order_domain_values(var, assignment):
            if self.is_valid(assignment, var, value):
                assignment[var] = value
                saved_domains = {c: list(self.domains[c]) for c in self.courses}
                
                # Apply forward checking if using MRV or Degree
                fc_success = True
                if self.use_mrv or self.use_degree:
                    fc_success = self.forward_check(assignment, var, value)
                
                if fc_success:
                    result, violations = self.backtrack(assignment)
                    if result is not None:
                        return result, violations
                
                # Backtrack
                assignment.pop(var)
                self.domains = saved_domains
        
        return None, 0
    
    def solve(self):
        return self.backtrack()

class TimetableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timetable Scheduler - 1CS Group")
        self.root.geometry("1000x700")
        
        # Define problem parameters
        self.days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        self.slots_per_day = {
            "Sunday": 5,
            "Monday": 5,
            "Tuesday": 3,  # Only morning slots
            "Wednesday": 5,
            "Thursday": 5
        }
        
        # Define time slots with actual timings
        self.time_slots = {
            1: "8:00-9:30",
            2: "9:30-11:00",
            3: "11:00-12:30",
            4: "13:30-15:00",
            5: "15:00-16:30"
        }
        
        # Tuesday has only 3 morning slots
        self.time_slots_tuesday = {
            1: "8:00-9:30",
            2: "9:30-11:00",
            3: "11:00-12:30"
        }
        
        self.rooms = ["Room A", "Room B", "Lab 1", "Lab 2"]
        
        # Define courses for one group (name, type, teacher(s))
        self.courses = [
            ("Sécurité", "Lecture", "Teacher 1"),
            ("Sécurité", "TD", "Teacher 1"),
            ("Méthodes formelles", "Lecture", "Teacher 2"),
            ("Méthodes formelles", "TD", "Teacher 2"),
            ("Analyse numérique", "Lecture", "Teacher 3"),
            ("Analyse numérique", "TD", "Teacher 3"),
            ("Entrepreneuriat", "Lecture", "Teacher 4"),
            ("Recherche opérationnelle 2", "Lecture", "Teacher 5"),
            ("Recherche opérationnelle 2", "TD", "Teacher 5"),
            ("Distributed Architecture", "Lecture", "Teacher 6"),
            ("Distributed Architecture", "TD", "Teacher 6"),
            ("Réseaux 2", "Lecture", "Teacher 7"),
            ("Réseaux 2", "TD", "Teacher 7"),
            ("Réseaux 2", "TP", ["Teacher 8", "Teacher 9", "Teacher 10"]),
            ("Artificial Intelligence", "Lecture", "Teacher 11"),
            ("Artificial Intelligence", "TD", "Teacher 11"),
            ("Artificial Intelligence", "TP", ["Teacher 12", "Teacher 13", "Teacher 14"]),
        ]
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title for single group
        ttk.Label(main_frame, text="1CS Group Timetable Generator", font=('Helvetica', 14, 'bold')).pack(pady=5)
        
        # Algorithm settings frame
        algo_frame = ttk.LabelFrame(main_frame, text="Algorithm Settings", padding="10")
        algo_frame.pack(fill=tk.X, pady=5)
        
        # Algorithm options
        self.use_ac3 = tk.BooleanVar(value=True)
        self.use_mrv = tk.BooleanVar(value=True)
        self.use_degree = tk.BooleanVar(value=False)
        self.use_lcv = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(algo_frame, text="Use AC3 preprocessing", variable=self.use_ac3).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(algo_frame, text="Use MRV", variable=self.use_mrv).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(algo_frame, text="Use Degree Heuristic", variable=self.use_degree).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(algo_frame, text="Use LCV", variable=self.use_lcv).pack(side=tk.LEFT, padx=5)
        
        # Run button
        ttk.Button(algo_frame, text="Generate Timetable", command=self.run_solver).pack(side=tk.RIGHT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="1CS Group Timetable", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Notebook for day tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create day tabs
        self.day_frames = {}
        for day in self.days:
            frame = ttk.Frame(self.notebook, padding="10")
            self.notebook.add(frame, text=day)
            self.day_frames[day] = frame
        
        # Teacher stats tab
        stats_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(stats_frame, text="Teacher Stats")
        self.stats_text = scrolledtext.ScrolledText(stats_frame, wrap=tk.WORD, height=10)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to generate timetable")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, pady=5)
    
    def display_timetable(self, solution):
        if not solution:
            messagebox.showerror("Error", "No solution found!")
            return
        
        # Clear previous content
        for day, frame in self.day_frames.items():
            for widget in frame.winfo_children():
                widget.destroy()
        
        # Populate each day's schedule with timing
        for day, frame in self.day_frames.items():
            columns = ("Time", "Course", "Type", "Teacher", "Room")
            tree = ttk.Treeview(frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120 if col == "Time" else 100)
            
            # Use appropriate time slots for each day
            slots = self.time_slots_tuesday if day == "Tuesday" else self.time_slots
            
            for slot, time in slots.items():
                slot_courses = []
                for course_id, (teacher, room, (course_day, course_slot)) in solution.items():
                    if course_day == day and course_slot == slot:
                        course_name = self.csp.course_data[course_id]['name']
                        course_type = self.csp.course_data[course_id]['type']
                        slot_courses.append((course_name, course_type, teacher, room))
                
                if not slot_courses:
                    tree.insert("", "end", values=(time, "Free", "", "", ""))
                else:
                    for course_name, course_type, teacher, room in slot_courses:
                        tree.insert("", "end", values=(time, course_name, course_type, teacher, room))
            
            vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_teacher_stats(solution)
    
    def update_teacher_stats(self, solution):
        self.stats_text.delete(1.0, tk.END)
        
        teacher_days = defaultdict(set)
        teacher_courses = defaultdict(list)
        for course_id, (teacher, _, (day, slot)) in solution.items():
            course_name = self.csp.course_data[course_id]['name']
            course_type = self.csp.course_data[course_id]['type']
            teacher_days[teacher].add(day)
            teacher_courses[teacher].append((course_name, course_type, day, slot))
        
        violations = sum(1 for days in teacher_days.values() if len(days) > 2)
        
        self.stats_text.insert(tk.END, f"Teacher Statistics for 1CS Group\n")
        self.stats_text.insert(tk.END, f"================================\n\n")
        self.stats_text.insert(tk.END, f"Total soft constraint violations: {violations}\n\n")
        
        for teacher in sorted(teacher_days.keys()):
            days = teacher_days[teacher]
            courses = teacher_courses[teacher]
            
            self.stats_text.insert(tk.END, f"{teacher}:\n")
            self.stats_text.insert(tk.END, f"  Workdays: {len(days)} ({', '.join(sorted(days))})\n")
            if len(days) > 2:
                self.stats_text.insert(tk.END, f"  SOFT CONSTRAINT VIOLATION: More than 2 workdays\n")
            
            self.stats_text.insert(tk.END, f"  Courses:\n")
            for course_name, course_type, day, slot in sorted(courses, key=lambda x: (x[2], x[3])):
                self.stats_text.insert(tk.END, f"    - {course_name} ({course_type}): {day}, Slot {slot}\n")
            self.stats_text.insert(tk.END, "\n")
    
    def run_solver(self):
        self.status_var.set("Solving timetable for 1CS group... This may take a moment.")
        self.root.update()
        
        self.csp = TimetableCSP(
            courses=self.courses,
            teachers=[f"Teacher {i}" for i in range(1, 15)],
            rooms=self.rooms,
            days=self.days,
            slots_per_day=self.slots_per_day,
            use_ac3=self.use_ac3.get(),
            use_mrv=self.use_mrv.get(),
            use_degree=self.use_degree.get(),
            use_lcv=self.use_lcv.get()
        )
        
        solution, violations = self.csp.solve()
        
        if solution:
            self.status_var.set(f"Solution found with {violations} soft constraint violations.")
            self.display_timetable(solution)
        else:
            self.status_var.set("No solution found.")
            messagebox.showerror("Error", "Could not find a valid timetable. Try different algorithm settings.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()