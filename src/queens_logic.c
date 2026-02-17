#define NULL ((void*)0)
#define MAX_POSSIBLE_SQUARE 676 //Max numbers of color for 26*26 board (kan batas max alfabet 26 yak)


// Callback type: receives size and a pointer to the flat solution array. So that C can communicate to Python for liveupdates
typedef int (*CallbackFunc)(int size, int* solution_flat);
// IterCount type: basically just reports the iter count to python since C cannot return 2 values in one function
typedef void (*IterCountFunc)(int itercount);

typedef struct {
    int row;
    int col;
} Node; // Node for BFS representing {row, col}
typedef struct Queue {
     Node arr[MAX_POSSIBLE_SQUARE];
     int head;
     int tail;
} Queue;

// Globals mainly for the Python layer
static int g_iteration_count = 0;
static int g_update_freq = 0;
static CallbackFunc interrupt_func = NULL;


static void init_queue(Queue* q){
    q->head = 0;
    q->tail = -1;
}

static int is_queue_empty(Queue* q){
    return q->head > q->tail;
}

static void enqueue(Queue* q, Node node){
    q->tail++;
    q->arr[q->tail] = node;
}

static Node dequeue(Queue* q){
    if(is_queue_empty(q)){
        Node empty = {-1, -1}; 
        return empty;
    }

    Node temp = q->arr[q->head];
    q->head++;
    
    if (q->head > q->tail) {
        q->head = 0;
        q->tail = -1;
    }
    
    return temp;
}


/**
 * @brief BFS search
 * @return 1 if reachable, 0 if not
 */
int BFS(Node start, Node goal, int size, char board[size][size]){
    Queue que; // que?
    init_queue(&que);
    int visited[size][size];
    for(int i = 0; i<size; i++){
        for(int j = 0; j<size; j++){
            visited[i][j] = 0;
        }
    }

    // Up down left right
    int dir_row[] = {-1,1,0,0};
    int dir_col[] = {0,0,-1,1};

    enqueue(&que, start);
    visited[start.row][start.col] = 1;

    while(!is_queue_empty(&que)){
        Node current = dequeue(&que);
        if(current.row == goal.row && current.col == goal.col){
            return 1;
        }
        for(int i = 0; i<4; i++){
            int new_row = current.row + dir_row[i]; 
            int new_col = current.col + dir_col[i];

            
            if( new_row>=0 && new_row<size && new_col>=0 && new_col<size && board[new_row][new_col]==board[start.row][start.col] && !visited[new_row][new_col]){
                visited[new_row][new_col] = 1;
                enqueue(&que,(Node){new_row,new_col});
            }

        }
    }

    return 0;
}

/**
 * @brief Check if there is any disconnected color islands using BFS :/
 * @return 1 If there is no disconnected islands, 0 if yes. Oh, also -1 if jumlah color != row or col
 */
static int check_board_islands(int size, char board[size][size]){
    int is_region_checked[256]; // Same as region occuped on solve_queen() but specialized for this
    int color_num = 0;
    unsigned char current_region = '\0';

    for(int i = 0; i<256; i++){ // Memset as usual
        is_region_checked[i] = 0; 
    }


    // Looks horrendous with 4 for-loops but will actually be pretty optimized since it'll skip
    // color islands that are already checked
    for(int i = 0; i<size; i++){
        for(int j = 0; j<size; j++){
            if(!is_region_checked[(unsigned char)board[i][j]]){
                color_num++;
                current_region = (unsigned char)board[i][j];
                

                for(int k = i; k<size; k++){
                    int l = (k==i) ? (j+1):0;
                    
                    for(l; l<size; l++){
                        if(board[k][l]==current_region){
                            Node start = {i,j};
                            Node goal = {k,l};
                            int result =BFS(start, goal, size, board);
                            if(!result) return 0; // Found a disconnected color island
                        }
                    }
                }

                is_region_checked[current_region] = 1;

            }
        }
    }
    if(color_num!=size){
        return -1;
    }
    return 1;
}

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


/**
 * @brief Recursion WITH early pruning
 */
static int solve_queen_recursion(int row, int col, int size, int solution[size][size], char board[size][size], int occupied_region[256]){
    
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

// So um, early pruning is not allowed... oh well here goes nothing

static int is_safe_check_but_a_bit_different(int row, int col, int size, int solution[size][size], char board[size][size]) {
    
    /* == Row col check ==*/
    for (int k = 0; k < size; k++) {
        if (k != row && solution[k][col] == 1) return 0;
        if (k != col && solution[row][k] == 1) return 0;
    }

    /* == Region Check == */
    char current_region = board[row][col];
    for (int r = 0; r < size; r++) {
        for (int c = 0; c < size; c++) {
            if (r == row && c == col) continue; // Skip self
            if (solution[r][c] == 1 && board[r][c] == current_region) return 0;
        }
    }

    /* == Adjacency checks == */
    int ulc, urc, blc, brc; // Upper-left-corner, upper-right-corner, etc..
    ulc = (col>0) && (row>0);
    urc = (col<size-1) && (row>0);
    blc = (col>0) && (row<size-1);
    brc = (col<size-1) && (row<size-1);

    if(ulc && solution[row-1][col-1]) return 0;
    if(urc && solution[row-1][col+1]) return 0;
    if(blc && solution[row+1][col-1]) return 0;
    if(brc && solution[row+1][col+1]) return 0;

    return 1;
}

static int is_whole_board_valid(int size, int solution[size][size], char board[size][size]) {
    for(int r = 0; r < size; r++) {
        for(int c = 0; c < size; c++) {
            if(solution[r][c] == 1) {
                // If any queen is unsafe, the whole board is invalid
                if (!is_safe_check_but_a_bit_different(r, c, size, solution, board)) return 0;
            }
        }
    }
    return 1;
}

/**
 * @brief Recursion without early pruning. Generates full board, then checks validity.
 */
static int solve_slow_recursion(int row, int size, int solution[size][size], char board[size][size]){
    /* == LIVE UPDATE LOGIC == */
    g_iteration_count++;
    if (interrupt_func != NULL && g_update_freq > 0) {
        if (g_iteration_count % g_update_freq == 0) {
            if(!interrupt_func(size, (int*)solution)){
                return -1; 
            }
        }
    }

    // Base Case
    if (row == size) {
        if (is_whole_board_valid(size, solution, board)) {
            return 1;
        }
        return 0;
    }

    int result; 


    for (int col = 0; col < size; col++){
        solution[row][col] = 1;
        
        result = solve_slow_recursion(row + 1, size, solution, board);
        
        if (result == 1) {
            return 1;
        }
        else if (result == -1){
            return -1;
        }
        
        // Backtrack
        solution[row][col] = 0;
    }

    return 0;
}


int solve_queens(int size, char board[size][size], int solution[size][size], int freq, CallbackFunc cb, IterCountFunc itcountfun, int isPrune){
    int occupied_region[256];

    // Setup globals
    g_iteration_count = 0;
    g_update_freq = freq;
    interrupt_func = cb;

    // Memsets
    for(int i = 0; i<size; i++){for(int j = 0; j<size; j++){solution[i][j] = 0;}}
    for(int i = 0; i<256; i++){occupied_region[i] = 0;}
    
    int board_validity = check_board_islands(size,board);
    if(board_validity==0){
        return -2; // Board islands disconnected
    }
    else if(board_validity==-1){
        return -3; // Board colors amount != row or col
    }

    int result;
    if(isPrune){
        result = solve_queen_recursion(0, 0, size, solution, board, occupied_region);
    }
    else{
        result = solve_slow_recursion(0, size, solution, board);
    }
    
    itcountfun(g_iteration_count);
    return result;
}