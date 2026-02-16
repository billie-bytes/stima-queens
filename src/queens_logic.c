#define NULL ((void*)0)


// Callback type: receives size and a pointer to the flat solution array. So that C can communicate to Python for liveupdates
typedef int (*CallbackFunc)(int size, int* solution_flat);
// IterCount type: basically just reports the iter count to python since C cannot return 2 values in one function
typedef void (*IterCountFunc)(int itercount);

static int g_iteration_count = 0;
static int g_update_freq = 0;
static CallbackFunc interrupt_func = NULL;
static CallbackFunc iteration_count_report = NULL;

static int is_safe(int i, int j, int size, int solution[size][size], char board[size][size], int occupied_region[256]){
    /* == Row-col check == */
    for(int _i = 0; _i<size; _i++){
        if(solution[_i][j]==1){
            return 0;
        }
    }
    for(int _j = 0; _j<size; _j++){
        if(solution[i][_j]==1){
            return 0;
        }
    }

    /* == Adjacency checks == */
    int ulc, urc, blc, brc; // Upper-left-corner, upper-right-corner, etc..
    ulc = (j>0) && (i>0);
    urc = (j<size-1) && (i>0);
    blc = (j>0) && (i<size-1);
    brc = (j<size-1) && (i<size-1);

    if(ulc && solution[i-1][j-1]) return 0;
    if(urc && solution[i-1][j+1]) return 0;
    if(blc && solution[i+1][j-1]) return 0;
    if(brc && solution[i+1][j+1]) return 0;

    /* == Region check == */
    if(occupied_region[(unsigned char)board[i][j]]==1) return 0;

    return 1;
}

int solve_queen_recursion(int row, int col, int size, int solution[size][size], char board[size][size], int occupied_region[256]){
    
    /* == LIVE UPDATE LOGIC == */
    g_iteration_count++;
    if (interrupt_func != NULL && g_update_freq > 0) {
        if (g_iteration_count % g_update_freq == 0) {
            // Cast 2D array to flat pointer for Python
            if(!interrupt_func(size, (int*)solution)){
                return -1; // To stop the recursion dead in its tracks and return a special code (-1) for error in python
            }
        }
    }

    int result;

    // Base cases (I didnt add a check for queen num == region num but it already works just fine I thunk)
    if(row==size) return 1;
    else if (col==size) return 0;
    
    if(is_safe(row,col,size,solution,board,occupied_region)){
        occupied_region[(unsigned char)board[row][col]] = 1;
        solution[row][col] = 1;
        result = solve_queen_recursion(row+1, 0, size, solution, board, occupied_region);
    }
    else return solve_queen_recursion(row, col+1, size, solution, board, occupied_region);
    
    if(result==1){
        return 1;
    }
    else if(result == -1){
        return -1;
    }
    else{
        // Traceback and cleaning up the footprints (solution matrix and occupied regions)
        solution[row][col] = 0;
        occupied_region[(unsigned char)board[row][col]] = 0;
        return solve_queen_recursion(row, col+1, size, solution, board, occupied_region);
    }
}

int solve_queens(int size, char board[size][size], int solution[size][size], int freq, CallbackFunc cb, IterCountFunc itcountfun){
    int occupied_region[256];

    // Setup globals
    g_iteration_count = 0;
    g_update_freq = freq;
    interrupt_func = cb;

    // Memsets
    for(int i = 0; i<size; i++){for(int j = 0; j<size; j++){solution[i][j] = 0;}}
    for(int i = 0; i<256; i++){occupied_region[i] = 0;}
    
    int result = solve_queen_recursion(0, 0, size, solution, board, occupied_region);


    itcountfun(g_iteration_count);
    return result;
}