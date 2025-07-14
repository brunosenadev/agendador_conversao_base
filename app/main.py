from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, time
from database import engine, SessionLocal
from models import Agendamento, Base
from sqlalchemy import desc

app = FastAPI()
Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.post("/cad_agendamento/criar")
def agendar(request: Request,
            cliente: str = Form(...),
            unificado: bool = Form(False),
            sisplan_web: bool = Form(False),
            data_conversao: str = Form(...),
            ultimo_dia_trabalho: str = Form(""),
            horario_trabalho: str = Form(""),
            valor: str = Form("0"),
            conexao: str = Form("")):
    db = SessionLocal()
    novo = Agendamento(
        cliente=cliente,
        unificado=unificado,
        sisplan_web=sisplan_web,
        data_conversao=datetime.strptime(data_conversao, "%Y-%m-%d").date(),
        ultimo_dia_trabalho=ultimo_dia_trabalho,
        horario_trabalho=datetime.strptime(horario_trabalho, "%H:%M").time() if horario_trabalho else None,
        valor=valor.replace(",", "."),
        conexao=conexao
    )
    db.add(novo)
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/cad_agendamento", response_class=HTMLResponse)
def cadastro_agendamentos(request: Request):
    return templates.TemplateResponse("cad_agendamento.html", {"request": request })


@app.get("/", response_class=HTMLResponse)
def lista_agendamentos(request: Request, data_de: str = "", data_ate: str = ""):
    db = SessionLocal()
    query = db.query(Agendamento)

    if data_de:
        try:
            data_convertida = datetime.strptime(data_de, "%Y-%m-%d").date()
            query = query.filter(Agendamento.data_conversao >= data_convertida)
        except ValueError:
            pass  
    
    if data_ate:
        try:
            data_convertida_ate = datetime.strptime(data_ate, "%Y-%m-%d").date()
            query = query.filter(Agendamento.data_conversao <= data_convertida_ate)
        except ValueError:
            pass

    dados = query.order_by(desc(Agendamento.id)).all()

    total = len(dados)
    concluidos = len([d for d in dados if d.concluido])
    try:
        valor_total = sum(float(d.valor.replace(",", ".") or 0) for d in dados)
    except Exception:
        valor_total = 0.0

    db.close()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "agendamentos": dados,
        "total": total,
        "concluidos": concluidos,
        "valor_total": valor_total,
        "data_de": data_de,
        "data_ate": data_ate  
    })
@app.post("/remover/{agendamento_id}")
def remover_agendamento(agendamento_id: int, request: Request):
    db = SessionLocal()
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        db.close()
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    db.delete(agendamento)
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)

@app.post("/concluir/{agendamento_id}")
def atualiza_agendamento(agendamento_id: int, request: Request):
    db = SessionLocal()
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        db.close()
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    agendamento.concluido = 1
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_config=None)
