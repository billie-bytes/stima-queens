import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import ctypes
import numpy as np
import time

from image_io import process_board_input, generate_board_output, create_board_from_text

# Callback type: receives size and a pointer to the flat solution array. So that C can communicate to Python for liveupdates
CALLBACK_TYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
ITER_COUNT_TYPE = ctypes.CFUNCTYPE(None, ctypes.c_int)

class QueensSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens Region Solver")
        self.root.geometry("950x650")

        # Load the C stuff
        try:
            self.lib = ctypes.CDLL('./queens_logic.so') 
            self.lib.solve_queens.argtypes = [
                ctypes.c_int, # int size
                np.ctypeslib.ndpointer(dtype=np.int8, ndim=1, flags='C_CONTIGUOUS'), # char board[size][size]
                np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'), # int solution[size][size]
                ctypes.c_int, # int freq
                CALLBACK_TYPE, # CallbackFunc cb
                ITER_COUNT_TYPE, # IterCountFunc itcountfun
            ]
            self.lib.solve_queens.restype = ctypes.c_int
        except OSError:
            messagebox.showerror("Error", "Could not load .SO file.")
            self.root.destroy()
            return

        self.grid_size = 8
        self.current_image_path = None
        self.region_data = None
        self.step_counter = 0

        self.ui_stuff()

    def ui_stuff(self):
        # Top Frame
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        btn_load = tk.Button(control_frame, text="1. Load File (Img/Txt)", command=self.load_file, width=20, height=2)
        btn_load.pack(side=tk.LEFT, padx=10)

        # Step N Input
        lbl_step = tk.Label(control_frame, text="Live Update Every N Steps:", font=("Arial", 10))
        lbl_step.pack(side=tk.LEFT, padx=(20, 5))
        self.entry_step = tk.Entry(control_frame, width=8, font=("Arial", 10))
        self.entry_step.insert(0, "0") # Default 0 = disabled
        self.entry_step.pack(side=tk.LEFT, padx=(0, 20))
        
        lbl_note = tk.Label(control_frame, text="(0 to disable for speed benchmarks)", fg="gray", font=("Arial", 8))
        lbl_note.pack(side=tk.LEFT)

        btn_solve = tk.Button(control_frame, text="2. Solve Puzzle", command=self.solve_puzzle, width=20, height=2, bg="#dddddd")
        btn_solve.pack(side=tk.RIGHT, padx=20)

        # Main Frame
        image_frame = tk.Frame(self.root)
        image_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Left Panel
        self.panel_left = tk.Frame(image_frame, bg="white", width=400, height=400)
        self.panel_left.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.label_input_title = tk.Label(self.panel_left, text="Input Board", bg="white", font=("Arial", 12, "bold"))
        self.label_input_title.pack(side=tk.TOP, pady=5)
        self.label_input_img = tk.Label(self.panel_left, bg="#f0f0f0", text="No File Loaded")
        self.label_input_img.pack(expand=True, fill=tk.BOTH)

        # Right Panel
        self.panel_right = tk.Frame(image_frame, bg="white", width=400, height=400)
        self.panel_right.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)
        self.label_output_title = tk.Label(self.panel_right, text="Solution / Live View", bg="white", font=("Arial", 12, "bold"))
        self.label_output_title.pack(side=tk.TOP, pady=5)
        self.label_output_img = tk.Label(self.panel_right, bg="#f0f0f0")
        self.label_output_img.pack(expand=True, fill=tk.BOTH)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Board File",
            filetypes=[
                ("All Supported", "*.png *.jpg *.jpeg *.txt"),
                ("Images", "*.png *.jpg *.jpeg"),
                ("Text Files", "*.txt")
            ]
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith(".txt"):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Dimension calculations
                row_length = content.find('\n')
                string_length = len("".join(content.split()))
                if(string_length!=(row_length**2)):
                    raise ValueError(f"Each row must have the same number of characters!")
                for i in range(string_length):
                    if((i%(row_length+1)==row_length) and content[i]!='\n'):
                        raise ValueError(f"Each row must have the same number of characters!")
                self.grid_size = row_length

                # Create image from txt
                img_path, region_list = create_board_from_text(content, self.grid_size)
                self.current_image_path = img_path
                self.region_data = region_list
                print(f"Text processed. Image at {img_path}")
                self.display_image(self.current_image_path, self.label_input_img)

            else:
                # Handle Image Input
                self.current_image_path = file_path
                self.display_image(self.current_image_path, self.label_input_img)
                size_val = simpledialog.askinteger("Grid Size", "What is the size of the board? (e.g. 8)", minvalue=4, maxvalue=50)
                if not size_val:
                    return
                self.grid_size = size_val
                self.region_data = process_board_input(file_path, self.grid_size)
                print(f"Image processed for size {self.grid_size}.")

            # Display the input image
            self.label_input_title.config(text=f"Input (Size: {self.grid_size})")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {e}")

    def c_interrupt(self, size, solution_ptr):
        """
        Called from C library during recursion for liveupdates
        """
        try:
            solution_arr = np.ctypeslib.as_array(solution_ptr, shape=(size*size,))
            self.step_counter += 1
            file_path = f"output/process_step_{self.step_counter}.png"
            
            generate_board_output(self.current_image_path, solution_arr, file_path, size)
            
            # Update UI (Must update idletasks to refresh UI during blocking C call)
            self.display_image(file_path, self.label_output_img)
            self.root.update()
            return 1
        except Exception as e:
            print(f"Callback Error: {e}")
            return 0
        
    def c_iter_count(self, itercount):
        """
        Also called from C to report the iteration count
        """
        self.step_counter = itercount

    def save_text_solution(self, solution_array):
        """
        Saves the solution to a text file where '#' represents a queen.
        """
        try:
            with open("output/final_solution.txt", "w") as f:
                for r in range(self.grid_size):
                    row_str = ""
                    for c in range(self.grid_size):
                        idx = r * self.grid_size + c
                        if solution_array[idx] == 1:
                            row_str += "#"
                        else:
                            row_str += self.region_data[idx]
                    f.write(row_str + "\n")
            print("Text solution saved to output/final_solution.txt")
        except Exception as e:
            print(f"Failed to save text solution: {e}")

    def solve_puzzle(self):
        if not self.region_data:
            messagebox.showwarning("Warning", "Please load a file first.")
            return
        
        try:
            step_n = int(self.entry_step.get())
        except ValueError:
            step_n = 0

        self.step_counter = 0
        
        try:
            board_array = np.array([ord(c) for c in self.region_data], dtype=np.int8)
            solution_array = np.zeros(self.grid_size * self.grid_size, dtype=np.int32)

            # To pass inside the C component
            c_func = CALLBACK_TYPE(self.c_interrupt)
            c_iter_func = ITER_COUNT_TYPE(self.c_iter_count)

            # Sikat
            start_time = time.perf_counter()


            result = self.lib.solve_queens(self.grid_size, board_array, solution_array, step_n, c_func, c_iter_func)
            
            time_elapsed = time.perf_counter() - start_time

            # Final Output after liveupdates
            output_path = "output/final_solution.png"
            generate_board_output(self.current_image_path, solution_array, output_path, self.grid_size)
            self.display_image(output_path, self.label_output_img)
            self.save_text_solution(solution_array)
            
            if result == -1:
                return
            elif result == 0:
                messagebox.showinfo("Done", f"No solutions found :(")
            else:
                messagebox.showinfo("Done", f"Puzzle Solved in {time_elapsed*1000} miliseconds in {self.step_counter} iterations")
            
        except Exception as e:
            messagebox.showerror("Error", f"Solver failed: {e}")
            return

    def display_image(self, path, label_widget):
        img = Image.open(path)
        img.thumbnail((400, 400)) 
        tk_img = ImageTk.PhotoImage(img)
        
        label_widget.config(image=tk_img, text="")
        label_widget.image = tk_img 

if __name__ == "__main__":
    root = tk.Tk()
    app = QueensSolverApp(root)
    root.mainloop()