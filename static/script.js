
const boardElement = document.getElementById("board");
const statusElement = document.getElementById("status");

const pieces = {
    r:'♜', n:'♞', b:'♝', q:'♛', k:'♚', p:'♟',
    R:'♖', N:'♘', B:'♗', Q:'♕', K:'♔', P:'♙'
};

let selectedSquare = null;

let boardState = [
['r','n','b','q','k','b','n','r'],
['p','p','p','p','p','p','p','p'],
['','','','','','','',''],
['','','','','','','',''],
['','','','','','','',''],
['','','','','','','',''],
['P','P','P','P','P','P','P','P'],
['R','N','B','Q','K','B','N','R']
];

function renderBoard() {

    boardElement.innerHTML = "";

    for(let row = 0; row < 8; row++) {

        for(let col = 0; col < 8; col++) {

            const square = document.createElement("div");

            square.classList.add("square");

            if((row + col) % 2 === 0) {
                square.classList.add("light");
            } else {
                square.classList.add("dark");
            }

            square.dataset.row = row;
            square.dataset.col = col;

            const piece = boardState[row][col];

            square.textContent = pieces[piece] || "";

            if(
                selectedSquare &&
                selectedSquare.row === row &&
                selectedSquare.col === col
            ) {
                square.classList.add("selected");
            }

            square.addEventListener("click", onSquareClick);

            boardElement.appendChild(square);
        }
    }
}

async function onSquareClick(event) {

    const row = Number(event.currentTarget.dataset.row);
    const col = Number(event.currentTarget.dataset.col);

    const clickedPiece = boardState[row][col];

    // selecting piece
    if(selectedSquare === null) {

        if(clickedPiece !== "" && clickedPiece === clickedPiece.toUpperCase()) {

            selectedSquare = {
                row: row,
                col: col
            };

            renderBoard();
        }

        return;
    }

    // change selected piece
    if(clickedPiece !== "" && clickedPiece === clickedPiece.toUpperCase()) {

        selectedSquare = {
            row: row,
            col: col
        };

        renderBoard();

        return;
    }

    const move =
        convertPosition(selectedSquare.col) +
        convertRow(selectedSquare.row) +
        convertPosition(col) +
        convertRow(row);

    selectedSquare = null;

    renderBoard();

    try {

        const response = await fetch("/move", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                move: move
            })
        });

        const data = await response.json();

        if(data.error) {

            statusElement.innerText = data.error;
            return;
        }

        updateBoard(data.fen);

        statusElement.innerText =
            "AI Move: " + data.ai_move;

    } catch(error) {

        console.log(error);

        statusElement.innerText =
            "Move failed";
    }
}

function convertPosition(col) {

    const cols = ['a','b','c','d','e','f','g','h'];

    return cols[col];
}

function convertRow(row) {

    return 8 - row;
}

function updateBoard(fen) {

    const rows = fen.split(" ")[0].split("/");

    boardState = [];

    rows.forEach(row => {

        const currentRow = [];

        for(const char of row) {

            if(!isNaN(char)) {

                for(let i = 0; i < parseInt(char); i++) {
                    currentRow.push("");
                }

            } else {

                currentRow.push(char);
            }
        }

        boardState.push(currentRow);
    });

    renderBoard();
}

async function changeDifficulty() {

    const difficulty =
        document.getElementById("difficulty").value;

    await fetch("/set_difficulty", {
        method: "POST",
        headers: {
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            difficulty: difficulty
        })
    });

    statusElement.innerText =
        "Difficulty: " + difficulty;
}

async function resetGame() {

    await fetch("/reset");

    location.reload();
}

renderBoard();
