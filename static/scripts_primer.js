$(document).ready(function () {
    function addPrimerListToGroup(groupName, listName, listId) {
        var groupUl = document.getElementById(groupName);
        if (!groupUl) {
            var mainUl = document.getElementById('primer-lists');
            var groupLi = document.createElement('li');
            var groupA = document.createElement('a');
            groupA.textContent = groupName;
            groupLi.appendChild(groupA);
            groupUl = document.createElement('ul');
            groupUl.id = groupName;
            groupLi.appendChild(groupUl);
            mainUl.appendChild(groupLi);
        }

        var listLi = document.createElement('li');
        listLi.classList.add('primer-list-item');

        var listDiv = document.createElement('div');
        listDiv.style.display = 'flex';
        listDiv.style.alignItems = 'center';
        listDiv.style.justifyContent = 'space-between';

        var listA = document.createElement('a');
        listA.textContent = listName;
        listA.setAttribute('data-list-id', listId);
        listDiv.appendChild(listA);

        var iconContainer = document.createElement('div');

        var editIcon = document.createElement('span');
        editIcon.classList.add('icon', 'is-small', 'edit-button');
        editIcon.innerHTML = '<i class="fas fa-edit"></i>';
        editIcon.addEventListener('click', function(event) {
            event.stopPropagation();
            editPrimerList(listId);
        });
        iconContainer.appendChild(editIcon);

        var deleteIcon = document.createElement('span');
        deleteIcon.classList.add('icon', 'is-small', 'delete-button');
        deleteIcon.innerHTML = '<i class="fas fa-trash-alt"></i>';
        deleteIcon.addEventListener('click', function(event) {
            event.stopPropagation();
            deletePrimerList(listId);
        });
        iconContainer.appendChild(deleteIcon);

        listDiv.appendChild(iconContainer);
        listLi.appendChild(listDiv);

        groupUl.appendChild(listLi);

        listA.addEventListener('click', function () {
            document.querySelectorAll('.primer-list-item').forEach(function(item) {
                item.classList.remove('selected-list');
            });
            listLi.classList.add('selected-list');
            showPrimersForList(listId);
        });
    }

    function editPrimerList(listId) {
        console.log('Liste bearbeiten', listId);
        // Hier den Code zum Bearbeiten der Liste hinzufügen
    }

    function deletePrimerList(listId) {
        if (confirm('Bist du sicher, dass du diese Liste löschen möchtest?')) {
            console.log('Liste löschen', listId);
            fetch('/delete_primer_list/' + listId, {
                method: 'DELETE',
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.querySelector('.primer-list-item[data-list-id="' + listId + '"]').remove();
                    var notification = '<div class="notification is-success">Primer-Liste erfolgreich gelöscht!</div>';
                    $('.section').prepend(notification);
                    setTimeout(function() {
                        $('.notification.is-success').fadeOut();
                    }, 3000);
                } else {
                    console.error('Fehler beim Löschen der Primer-Liste:', data.message);
                }
            })
            .catch(error => {
                console.error('Fehler beim Löschen der Primer-Liste:', error);
            });
        }
    }

    function showPrimersForList(listId) {
        console.log('Zeige Primer für Liste:', listId);
        $.ajax({
            url: '/get-primers-for-list/' + listId,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                var newTable = $('#PrimerTable').DataTable();
                newTable.clear().draw();
                data.forEach(function(primer) {
                    newTable.row.add([
                        primer.application,
                        primer.pcr,
                        primer.target,
                        primer.oligos,
                        primer.sequence,
                        primer.box,
                        primer.position,
                        primer.reference,
                        primer.comment
                    ]).draw();
                });
            },
            error: function(error) {
                console.error("Fehler beim Abrufen der Primer:", error);
            }
        });
    }

    function openModal() {
        document.getElementById('modal').classList.add('is-active');
    }

    function closeModal() {
        document.getElementById('modal').classList.remove('is-active');
    }

    function savePrimerList() {
        var form = document.getElementById('new-primer-list-form');
        var formData = new FormData(form);

        fetch('/add_primer_list', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                closeModal();
                addPrimerListToGroup(data.primer_list.visibility, data.primer_list.name, data.primer_list.id);
                var notification = '<div class="notification is-success">Primer-Liste erfolgreich erstellt!</div>';
                $('.section').prepend(notification);
                setTimeout(function() {
                    $('.notification.is-success').fadeOut();
                }, 3000);
            } else {
                console.error('Fehler beim Speichern der Primer-Liste:', data.message);
            }
        })
        .catch(error => {
            console.error('Fehler beim Speichern der Primer-Liste:', error);
        });
    }

    function loadPrimerLists() {
        $.ajax({
            url: '/get_primer_lists',
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                data.forEach(function (primer_list) {
                    addPrimerListToGroup(primer_list.visibility, primer_list.name, primer_list.id);
                });
            },
            error: function (error) {
                console.error("Fehler beim Abrufen der Primer-Listen:", error);
            }
        });
    }

    loadPrimerLists();

    $('#PrimerTable').DataTable({
        paging: false,
        searching: false,
        bInfo: false,
        ordering: false,
        scrollCollapse: true,
        scrollY: '50vh'
    });

    document.getElementById('open-modal-button').addEventListener('click', openModal);
    document.getElementById('close-modal-button').addEventListener('click', closeModal);
    document.getElementById('save-primer-list-button').addEventListener('click', savePrimerList);
});
