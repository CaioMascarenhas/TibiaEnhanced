"use client";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const items = [
  [
    "O aplicativo é gratuito?",
    "Sim. Você pode usar todos os recursos gratuitamente. Se quiser apoiar o desenvolvimento, a seção Apoiar do aplicativo oferece contribuições voluntárias.",
  ],
  [
    "Preciso instalar Python ou criar uma conta?",
    "Não. O instalador e o ZIP portátil já incluem o necessário para abrir o aplicativo. As configurações ficam no seu computador, organizadas por perfil.",
  ],
  [
    "Como os recortes funcionam?",
    "Você escolhe a janela do Tibia e marca uma área. O compositor do Windows espelha essa região em uma janela flutuante, que você pode mover, ampliar e deixar transparente. Mantenha a janela de origem aberta; minimizar ou fechar o cliente pode interromper o espelho.",
  ],
  [
    "Os timers detectam ações dentro do jogo?",
    "Os alertas são iniciados por você. Eles contam o tempo configurado e tocam o som escolhido, sem detectar ações ou executar comandos no Tibia. Ao abrir o aplicativo ou trocar de perfil, os timers começam parados.",
  ],
  [
    "O Tibia Enhanced altera o cliente?",
    "O app usa miniaturas do compositor do Windows para os recortes. Não lê memória ou tráfego do cliente, não injeta código e não executa ações do jogo. É um projeto independente, sem afiliação ou aprovação da CipSoft; consulte as regras oficiais do Tibia ao avaliar o uso.",
  ],
];
export function FAQ() {
  return (
    <Accordion type="single" collapsible className="faq-list">
      {items.map(([title, text], i) => (
        <AccordionItem value={`faq-${i}`} key={title}>
          <AccordionTrigger>{title}</AccordionTrigger>
          <AccordionContent>{text}</AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}
