import { initializeApp } from "https://www.gstatic.com/firebasejs/9.1.3/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.1.3/firebase-auth.js";
import { getDatabase, ref, set, push, onChildAdded, onValue } from "https://www.gstatic.com/firebasejs/9.1.3/firebase-database.js";

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBwnPr1Fbts5447dBvreOiPiTADGtuxAd8",
    authDomain: "youjichat23.firebaseapp.com",
    databaseURL: "https://youjichat23.firebaseio.com",
    projectId: "youjichat23",
    storageBucket: "youjichat23.appspot.com",
    messagingSenderId: "393521013873",
    appId: "1:393521013873:web:9cd3f7e2df7bd6ffe2e7d0"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getDatabase(app);

// Sign Up
document.getElementById('signUpButton').addEventListener('click', () => {
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const userId = userCredential.user.uid;
            set(ref(db, 'users/' + userId), {
                firstName: firstName,
                lastName: lastName,
                email: email
            });
            alert("تم إنشاء الحساب!");
            document.getElementById('auth').style.display = 'none';
            document.getElementById('chat').style.display = 'block';
        })
        .catch((error) => {
            alert("خطأ: " + error.message);
        });
});

// Login
document.getElementById('loginButton').addEventListener('click', () => {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    signInWithEmailAndPassword(auth, email, password)
        .then(() => {
            alert("تم تسجيل الدخول بنجاح!");
            document.getElementById('auth').style.display = 'none';
            document.getElementById('chat').style.display = 'block';
            loadFriends();
        })
        .catch((error) => {
            alert("خطأ: " + error.message);
        });
});

// Sending messages
document.getElementById('sendMessageButton').addEventListener('click', () => {
    const message = document.getElementById('messageInput').value;
    const userId = auth.currentUser.uid;

    push(ref(db, 'messages'), {
        userId: userId,
        message: message,
        timestamp: Date.now()
    });

    document.getElementById('messageInput').value = '';
});

// Displaying messages
onChildAdded(ref(db, 'messages'), (snapshot) => {
    const data = snapshot.val();
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.textContent = data.message;
    messagesDiv.appendChild(messageDiv);
});

// Loading friends
function loadFriends() {
    const friendsList = document.getElementById('friendsList');
    onValue(ref(db, 'users'), (snapshot) => {
        friendsList.innerHTML = ''; // Clear existing list
        snapshot.forEach((childSnapshot) => {
            const childData = childSnapshot.val();
            const friendDiv = document.createElement('div');
            friendDiv.textContent = `${childData.firstName} ${childData.lastName}`;
            friendsList.appendChild(friendDiv);
        });
    });
}

// Searching for friends
document.getElementById('searchButton').addEventListener('click', () => {
    const query = document.getElementById('search').value.toLowerCase();
    const friendsList = document.getElementById('friendsList').children;

    Array.from(friendsList).forEach(friend => {
        const name = friend.textContent.toLowerCase();
        friend.style.display = name.includes(query) ? '' : 'none';
    });
});
