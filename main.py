import flet as ft
import os
import shutil
from pathlib import Path

# Percorso della cartella principale
BASE_DIR = Path(__file__).parent / "EZNotes_Data"
BASE_DIR.mkdir(exist_ok=True)

def main(page: ft.Page):
    page.title = "I miei Appunti (Flet)"
    page.theme_mode = ft.ThemeMode.DARK
    
    vaults_data = {}  # dizionario dinamico 

    current_vault = ""
    is_editing = False 
    
    show_vault_adder = False
    show_note_adder = False
    
    vault_to_rename = ""
    note_to_rename_idx = -1

    vault_input_field = ft.TextField(label="Nome del nuovo Vault", expand=True, text_size=14)
    note_input_field = ft.TextField(label="Titolo della nuova Nota", expand=True, text_size=14)
    
    rename_vault_field = ft.TextField(label="Nuovo nome Vault", expand=True, text_size=14)
    rename_note_field = ft.TextField(label="Nuovo titolo Nota", expand=True, text_size=14)


    # FUNZIONI DI LETTURA E SCRITTURA SU DISCO
    def carica_dati_da_disco():
        vaults_data.clear()
        for item in BASE_DIR.iterdir():
            if item.is_dir():
                vault_name = item.name
                vaults_data[vault_name] = []
                for file in item.glob("*.md"):
                    if file.is_file():
                        with open(file, "r", encoding="utf-8") as f:
                            content = f.read()
                        vaults_data[vault_name].append({
                            "title": file.stem, 
                            "content": content
                        })

    carica_dati_da_disco()


    # FUNZIONI DI LOGICA (CREAZIONE)
    def add_vault_confirm(e):
        nonlocal show_vault_adder
        name = vault_input_field.value.strip()
        if name and name not in vaults_data:
            (BASE_DIR / name).mkdir(exist_ok=True)
            vault_input_field.value = ""
            show_vault_adder = False
            carica_dati_da_disco()
            render_views()

    def add_note_confirm(e):
        nonlocal show_note_adder
        title = note_input_field.value.strip()
        if title:
            note_path = BASE_DIR / current_vault / f"{title}.md"
            with open(note_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\nInizia a scrivere qui...")
            note_input_field.value = ""
            show_note_adder = False
            carica_dati_da_disco()
            render_views()


    # FUNZIONI DI LOGICA (ELIMINAZIONE)
    def delete_vault(vault_name):
        vault_path = BASE_DIR / vault_name
        if vault_path.exists():
            shutil.rmtree(vault_path) # Rimuove la cartella e tutto il suo contenuto
            carica_dati_da_disco()
            render_views()

    def delete_note(note_idx):
        note_title = vaults_data[current_vault][note_idx]["title"]
        note_path = BASE_DIR / current_vault / f"{note_title}.md"
        if note_path.exists():
            note_path.unlink() # Elimina il file .md
            carica_dati_da_disco()
            render_views()


    # FUNZIONI DI LOGICA (RINOMINA)
    def rename_vault_confirm(e):
        nonlocal vault_to_rename
        new_name = rename_vault_field.value.strip()
        if new_name and new_name not in vaults_data:
            old_path = BASE_DIR / vault_to_rename
            new_path = BASE_DIR / new_name
            old_path.rename(new_path)
            vault_to_rename = ""
            carica_dati_da_disco()
            render_views()

    def rename_note_confirm(e):
        nonlocal note_to_rename_idx
        new_title = rename_note_field.value.strip()
        if new_title:
            old_title = vaults_data[current_vault][note_to_rename_idx]["title"]
            old_path = BASE_DIR / current_vault / f"{old_title}.md"
            new_path = BASE_DIR / current_vault / f"{new_title}.md"
            old_path.rename(new_path)
            note_to_rename_idx = -1
            carica_dati_da_disco()
            render_views()


    # GESTIONE VISIBILITÀ BARRE INLINE
    def toggle_vault_adder(e):
        nonlocal show_vault_adder
        show_vault_adder = not show_vault_adder
        render_views()

    def toggle_note_adder(e):
        nonlocal show_note_adder
        show_note_adder = not show_note_adder
        render_views()


    # INTERFACCIA GRAFICA (RENDERING)
    def render_views():
        page.views.clear()
        

        # Schermata 1: HOMEPAGE 
        if page.route == "/":
            # Barra per aggiungere Vault
            adder_row = ft.Row(
                controls=[
                    vault_input_field,
                    ft.IconButton(ft.Icons.CHECK, icon_color=ft.Colors.GREEN, on_click=add_vault_confirm),
                    ft.IconButton(ft.Icons.CLOSE, icon_color=ft.Colors.RED, on_click=toggle_vault_adder)
                ],
                visible=show_vault_adder,
                spacing=5
            )

            # Barra per rinominare Vault
            rename_row = ft.Row(
                controls=[
                    rename_vault_field,
                    ft.IconButton(ft.Icons.CHECK, icon_color=ft.Colors.GREEN, on_click=rename_vault_confirm),
                    ft.IconButton(ft.Icons.CLOSE, icon_color=ft.Colors.RED, on_click=lambda _: [setattr(rename_vault_field, "value", ""), render_views()])
                ],
                visible=bool(vault_to_rename),
                spacing=5
            )

            vault_buttons = []
            for vault_name in vaults_data.keys():
                def make_click_handler(name):
                    return lambda _: open_vault(name)
                def make_delete_handler(name):
                    return lambda _: delete_vault(name)
                def make_rename_trigger(name):
                    def _handler(e):
                        nonlocal vault_to_rename
                        vault_to_rename = name
                        rename_vault_field.value = name
                        render_views()
                    return _handler
                
                vault_buttons.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.FOLDER, color=ft.Colors.AMBER),
                        title=ft.Text(vault_name, size=18, weight=ft.FontWeight.BOLD),
                        on_click=make_click_handler(vault_name),
                        trailing=ft.Row(
                            controls=[
                                ft.IconButton(ft.Icons.EDIT_OUTLINED, on_click=make_rename_trigger(vault_name)),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=make_delete_handler(vault_name))
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            tight=True
                        )
                    )
                )

            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.AppBar(title=ft.Text("I miei Vault"), bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                        ft.Container(content=adder_row, padding=ft.Padding(20, 15, 20, 0)),
                        ft.Container(content=rename_row, padding=ft.Padding(20, 15, 20, 0)),
                        ft.ListView(controls=vault_buttons, expand=True, spacing=10, padding=20)
                    ],
                    floating_action_button=ft.FloatingActionButton(
                        icon=ft.Icons.ADD if not show_vault_adder else ft.Icons.CLOSE, 
                        bgcolor=ft.Colors.AMBER,
                        on_click=toggle_vault_adder 
                    )
                )
            )


        # Schermata 2: PAGINA DEL VAULT (Elenco delle Note)
        elif page.route == "/vault":
            nonlocal current_vault
            
            # Barra per aggiungere Nota
            adder_row = ft.Row(
                controls=[
                    note_input_field,
                    ft.IconButton(ft.Icons.CHECK, icon_color=ft.Colors.GREEN, on_click=add_note_confirm),
                    ft.IconButton(ft.Icons.CLOSE, icon_color=ft.Colors.RED, on_click=toggle_note_adder)
                ],
                visible=show_note_adder,
                spacing=5
            )

            # Barra per rinominare Nota
            rename_row = ft.Row(
                controls=[
                    rename_note_field,
                    ft.IconButton(ft.Icons.CHECK, icon_color=ft.Colors.GREEN, on_click=rename_note_confirm),
                    ft.IconButton(ft.Icons.CLOSE, icon_color=ft.Colors.RED, on_click=lambda _: [setattr(rename_note_field, "value", ""), render_views()])
                ],
                visible=(note_to_rename_idx != -1),
                spacing=5
            )

            note_buttons = []
            notes = vaults_data.get(current_vault, [])
            
            for index, note in enumerate(notes):
                def make_note_click_handler(idx):
                    return lambda _: open_note(idx)
                def make_note_delete(idx):
                    return lambda _: delete_note(idx)
                def make_note_rename_trigger(idx, title):
                    def _handler(e):
                        nonlocal note_to_rename_idx
                        note_to_rename_idx = idx
                        rename_note_field.value = title
                        render_views()
                    return _handler

                note_buttons.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ARTICLE, color=ft.Colors.BLUE_400),
                        title=ft.Text(note["title"], size=16),
                        on_click=make_note_click_handler(index),
                        trailing=ft.Row(
                            controls=[
                                ft.IconButton(ft.Icons.EDIT_OUTLINED, on_click=make_note_rename_trigger(index, note["title"])),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=make_note_delete(index))
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            tight=True
                        )
                    )
                )

            page.views.append(
                ft.View(
                    route="/vault",
                    controls=[
                        ft.AppBar(
                            title=ft.Text(f"Vault: {current_vault}"), 
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: go_to("/"))
                        ),
                        ft.Container(content=adder_row, padding=ft.Padding(15, 15, 15, 0)),
                        ft.Container(content=rename_row, padding=ft.Padding(15, 15, 15, 0)),
                        ft.ListView(controls=note_buttons, expand=True, spacing=5, padding=15)
                    ],
                    floating_action_button=ft.FloatingActionButton(
                        icon=ft.Icons.ADD if not show_note_adder else ft.Icons.CLOSE, 
                        bgcolor=ft.Colors.BLUE_400,
                        on_click=toggle_note_adder 
                    )
                )
            )

        # Schermata 3: Pagina della nota
        elif page.route.startswith("/note/"):
            note_index = int(page.route.split("/")[-1])
            note = vaults_data[current_vault][note_index]

            edit_field = ft.TextField(
                value=note["content"], 
                multiline=True, 
                expand=True,
                text_size=16,
                border=ft.InputBorder.NONE
            )

            def save_note(e):
                nonlocal is_editing
                note["content"] = edit_field.value 
                note_path = BASE_DIR / current_vault / f"{note['title']}.md"
                with open(note_path, "w", encoding="utf-8") as f:
                    f.write(edit_field.value)
                is_editing = False
                render_views()

            def toggle_edit(e):
                nonlocal is_editing
                is_editing = True
                render_views()

            content_display = edit_field if is_editing else ft.Markdown(
                value=note["content"],
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
            )

            action_button = ft.IconButton(ft.Icons.SAVE, on_click=save_note) if is_editing else ft.IconButton(ft.Icons.EDIT, on_click=toggle_edit)

            page.views.append(
                ft.View(
                    route=page.route,
                    controls=[
                        ft.AppBar(
                            title=ft.Text(note["title"]), 
                            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: go_to("/vault")),
                            actions=[action_button]
                        ),
                        ft.Container(
                            content=content_display,
                            padding=20,
                            expand=True
                        )
                    ]
                )
            )
            
        page.update()

    # Navigazione
    def go_to(route_name):
        nonlocal is_editing, show_vault_adder, show_note_adder, vault_to_rename, note_to_rename_idx
        is_editing = False 
        show_vault_adder = False 
        show_note_adder = False
        vault_to_rename = ""
        note_to_rename_idx = -1
        page.route = route_name
        render_views()

    def open_vault(vault_name):
        nonlocal current_vault
        current_vault = vault_name
        go_to("/vault")

    def open_note(note_index):
        go_to(f"/note/{note_index}")

    page.on_route_change = lambda e: render_views()
    page.route = "/"
    render_views()

ft.run(main)