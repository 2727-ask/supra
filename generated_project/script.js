// Constants and configuration
export const STORAGE_KEY = 'colorful-todo-tasks';

// DOM selectors
export const selectors = {
    input: '#new-task-input',
    addBtn: '#add-task-btn',
    list: '#task-list',
    filters: '#filters'
};

// State management
let tasks = [];
let currentFilter = 'all';

// Import Sortable for drag-and-drop functionality
import Sortable from 'https://cdn.jsdelivr.net/npm/sortablejs@latest/modular/sortable.core.esm.js';

// Utility functions
export function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

export function saveTasks() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

export function loadTasks() {
    const raw = localStorage.getItem(STORAGE_KEY);
    tasks = raw ? JSON.parse(raw) : [];
}

// State getters and setters for module encapsulation
export function getTasks() {
    return [...tasks];
}

export function setTasks(newTasks) {
    tasks = newTasks;
    saveTasks();
}

export function getCurrentFilter() {
    return currentFilter;
}

export function setCurrentFilter(filter) {
    currentFilter = filter;
}

// Task template renderer
export function renderTask({ id, text, completed }) {
    return `<li data-id='${id}' class='fadeIn'><input type='checkbox' class='task-check' ${completed ? 'checked' : ''}><span class='task-text ${completed ? 'completed' : ''}' contenteditable='false'>${text}</span><button class='edit-btn' aria-label='Edit'>✏️</button><button class='delete-btn' aria-label='Delete'>🗑️</button></li>`;
}

// Enable drag-and-drop functionality
export function enableDragging() {
    const list = document.querySelector(selectors.list);
    new Sortable(list, {
        animation: 150,
        onEnd(evt) {
            tasks.splice(evt.newIndex, 0, tasks.splice(evt.oldIndex, 1)[0]);
            saveTasks();
        }
    });
}

// Render all tasks based on current filter
export function renderAll() {
    const container = document.querySelector(selectors.list);
    container.innerHTML = '';
    const filtered = currentFilter === 'all' ? tasks : tasks.filter(t => (currentFilter === 'active' ? !t.completed : t.completed));
    filtered.forEach(t => container.insertAdjacentHTML('beforeend', renderTask(t)));
    attachEvents();
    enableDragging();
}

// Attach event listeners to task elements
export function attachEvents() {
    document.querySelectorAll('.task-check').forEach(cb => cb.addEventListener('change', toggleTask));
    document.querySelectorAll('.delete-btn').forEach(btn => btn.addEventListener('click', deleteTask));
    document.querySelectorAll('.edit-btn').forEach(btn => btn.addEventListener('click', enableEdit));
}

// Task operations
export function addTask() {
    const input = document.querySelector(selectors.input);
    const text = input.value.trim();
    if (!text) return;
    const task = { id: generateId(), text, completed: false };
    tasks.unshift(task);
    saveTasks();
    input.value = '';
    renderAll();
}

export function toggleTask(e) {
    const id = e.target.closest('li').dataset.id;
    const task = tasks.find(t => t.id === id);
    task.completed = !task.completed;
    saveTasks();
    renderAll();
}

export function deleteTask(e) {
    const li = e.target.closest('li');
    li.classList.add('fadeOut');
    li.addEventListener('animationend', () => {
        tasks = tasks.filter(t => t.id !== li.dataset.id);
        saveTasks();
        renderAll();
    });
}

// Enable editing functionality for tasks
export function enableEdit(e) {
    const span = e.target.closest('li').querySelector('.task-text');
    span.contentEditable = true;
    span.focus();
    const end = span.textContent.length;
    window.getSelection().collapse(span.childNodes[0], end);
    span.addEventListener('blur', () => {
        span.contentEditable = false;
        const id = span.closest('li').dataset.id;
        const task = tasks.find(t => t.id === id);
        task.text = span.textContent.trim();
        saveTasks();
        renderAll();
    }, { once: true });
}

// Filter functionality
export function setFilter(e) {
    if (e.target.tagName !== 'BUTTON') return;
    currentFilter = e.target.dataset.filter;
    document.querySelectorAll('#filters button').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    renderAll();
}

// Initialize the application
export function init() {
    loadTasks();
    document.querySelector(selectors.addBtn).addEventListener('click', addTask);
    document.querySelector(selectors.input).addEventListener('keydown', e => {
        if (e.key === 'Enter') addTask();
    });
    document.querySelector(selectors.filters).addEventListener('click', setFilter);
    document.querySelector(selectors.filters + " button[data-filter='all']").classList.add('active');
    renderAll();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);