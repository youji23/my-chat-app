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
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.database();

// Sign Up
document.getElementById('signUpButton').addEventListener('click', () => {
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    auth.createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            const userId = userCredential.user.uid;
            firebase.database().ref('users/' + userId).set({
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

    auth.signInWithEmailAndPassword(email, password)
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

    firebase.database().ref('messages').push({
        userId: userId,
        message: message,
        timestamp: Date.now()
    });

    document.getElementById('messageInput').value = '';
});

// Displaying messages
firebase.database().ref('messages').on('child_added', (snapshot) => {
    const data = snapshot.val();
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.textContent = data.message;
    messagesDiv.appendChild(messageDiv);
});

// Loading friends
function loadFriends() {
    const friendsList = document.getElementById('friendsList');
    firebase.database().ref('users').on('value', (snapshot) => {
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
document.getElementById('search').addEventListener('input', () => {
    const query = document.getElementById('search').value.toLowerCase();
    const friendsList = document.getElementById('friendsList').children;

    Array.from(friendsList).forEach(friend => {
        const name = friend.textContent.toLowerCase();
        friend.style.display = name.includes(query) ? '' : 'none';
    });
});
