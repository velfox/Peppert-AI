document.addEventListener("DOMContentLoaded", function() {
    loadAssistants();
});

async function loadAssistants() {
    try {
        const response = await fetch('/api/assistants');
        const assistants = await response.json();
        const assistantsList = document.getElementById('assistants-list');
        assistantsList.innerHTML = '';
        assistants.forEach(assistant => {
            const listItem = document.createElement('li');
            listItem.textContent = `${assistant.name} - ${assistant.description}`;
            const editButton = document.createElement('button');
            editButton.textContent = 'Edit';
            editButton.onclick = () => editAssistant(assistant);
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.onclick = () => deleteAssistant(assistant.id);
            listItem.appendChild(editButton);
            listItem.appendChild(deleteButton);
            assistantsList.appendChild(listItem);
        });
    } catch (error) {
        console.error('Error loading assistants:', error);
    }
}

async function addAssistant() {
    const name = document.getElementById('name').value;
    const description = document.getElementById('description').value;
    const instructions = document.getElementById('instructions').value;
    const model = 'gpt-4o'; // Autofill model
    try {
        const response = await fetch('/api/assistants', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, description, instructions, model }),
        });
        if (response.ok) {
            loadAssistants();
        } else {
            console.error('Error adding assistant:', response.statusText);
        }
    } catch (error) {
        console.error('Error adding assistant:', error);
    }
}

async function editAssistant(assistant) {
    const name = prompt('Enter new name:', assistant.name);
    const description = prompt('Enter new description:', assistant.description);
    const instructions = prompt('Enter new instructions:', assistant.instructions);
    const model = assistant.model; // Keep the model the same
    if (name && description && instructions) {
        try {
            const response = await fetch(`/api/assistants/${assistant.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, description, instructions, model }),
            });
            if (response.ok) {
                loadAssistants();
            } else {
                console.error('Error editing assistant:', response.statusText);
            }
        } catch (error) {
            console.error('Error editing assistant:', error);
        }
    }
}

async function deleteAssistant(id) {
    if (confirm('Are you sure you want to delete this assistant?')) {
        try {
            const response = await fetch(`/api/assistants/${id}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                loadAssistants();
            } else {
                console.error('Error deleting assistant:', response.statusText);
            }
        } catch (error) {
            console.error('Error deleting assistant:', error);
        }
    }
}
