import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

interface Bolsista {
  nome: string;
  curso: string;
  programa: string;
  supervisor: string;
  email: string;
  presente: number;
  faltas: number;
  carga_horaria: number;
  registros: number;
  percentual: number;
  status: string;
}

interface Acao {
  title: string;
  description: string;
  url: string;
}

interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done';
}

@Component({
  standalone: true,
  selector: 'app-root',
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css'],
})
export class App {
  protected readonly title = signal('Portal de Bolsista');
  protected readonly bolsista = signal<Bolsista | null>(null);
  protected readonly acoes = signal<Acao[]>([]);
  protected readonly status = signal('Clique em um botão para carregar os dados.');
  protected readonly tasks = signal<Task[]>([]);
  protected draggedTaskId: number | null = null;
  protected draggedEl: HTMLElement | null = null;

  protected async loadTasks() {
    try {
      const res = await fetch('http://localhost:8000/api/tasks/');
      const json = await res.json();
      this.tasks.set(json.tasks || []);
    } catch (err) {
      console.error(err);
    }
  }

  protected async createTask() {
    const title = prompt('Título da tarefa');
    if (!title) return;
    try {
      const res = await fetch('http://localhost:8000/api/tasks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      const json = await res.json();
      this.tasks.set([...(this.tasks() || []), json.task]);
    } catch (err) {
      console.error(err);
    }
  }

  protected async moveTask(id: number, status: string) {
    try {
      await fetch(`http://localhost:8000/api/tasks/${id}/move/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      await this.loadTasks();
    } catch (err) {
      console.error(err);
    }
  }

  protected async associateTask(taskId: number) {
    const freqId = prompt('ID da frequência para associar');
    if (!freqId) return;
    try {
      await fetch(`http://localhost:8000/api/tasks/${taskId}/associate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ frequency_id: Number(freqId) }),
      });
      alert('Associada');
    } catch (err) {
      console.error(err);
    }
  }

  protected onDragStart(ev: DragEvent, id: number) {
    this.draggedTaskId = id;
    try {
      ev.dataTransfer?.setData('text/plain', String(id));
      if (ev.dataTransfer) ev.dataTransfer.effectAllowed = 'move';
      this.draggedEl = ev.target as HTMLElement;
      this.draggedEl?.classList.add('dragging');
    } catch (e) {
      // ignore
    }
  }

  protected onDragOver(ev: DragEvent) {
    ev.preventDefault();
  }

  protected async onDrop(ev: DragEvent, status: string) {
    ev.preventDefault();
    const idStr = ev.dataTransfer?.getData('text/plain') || String(this.draggedTaskId || '');
    const id = Number(idStr);
    if (!id) return;
    // feedback visual na coluna
    const target = ev.currentTarget as HTMLElement | null;
    if (target) {
      target.classList.remove('drag-over');
      target.classList.add('dropped');
      setTimeout(() => target.classList.remove('dropped'), 350);
    }
    await this.moveTask(id, status);
    this.draggedTaskId = null;
  }

  protected onDragEnter(ev: DragEvent) {
    const target = ev.currentTarget as HTMLElement | null;
    if (target) target.classList.add('drag-over');
  }

  protected onDragLeave(ev: DragEvent) {
    const target = ev.currentTarget as HTMLElement | null;
    if (target) target.classList.remove('drag-over');
  }

  protected onDragEnd(ev: DragEvent) {
    this.draggedTaskId = null;
    if (this.draggedEl) this.draggedEl.classList.remove('dragging');
    this.draggedEl = null;
  }

  protected async loadBolsista() {
    this.status.set('Carregando dados do bolsista...');
    try {
      const response = await fetch('http://localhost:8000/api/bolsista/');
      const json = await response.json();
      this.bolsista.set(json.bolsista);
      this.status.set('Dados do bolsista carregados.');
    } catch (error) {
      this.status.set('Erro ao carregar os dados do bolsista.');
      console.error(error);
    }
  }

  protected async loadAcoes() {
    this.status.set('Carregando ações...');
    try {
      const response = await fetch('http://localhost:8000/api/acoes/');
      const json = await response.json();
      this.acoes.set(json.acoes || []);
      this.status.set('Ações carregadas.');
    } catch (error) {
      this.status.set('Erro ao carregar ações.');
      console.error(error);
    }
  }

  protected goToDjango() {
    window.location.href = 'http://localhost:8000';
  }

  protected openAcao(acao: Acao) {
    window.open(acao.url, '_blank');
  }
}
