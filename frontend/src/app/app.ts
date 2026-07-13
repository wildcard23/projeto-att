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
