#!/usr/bin/python3

import sqlite3
from datetime import date, datetime

import humanize
import markdown2
from flask import Flask, render_template, request, url_for
from markupsafe import Markup
from pydantic import BaseModel
from wtforms import DateField, Form, StringField, validators

app = Flask(__name__, static_folder="static")


class FormData(BaseModel):
    name: str
    date_of_birth: date
    date_of_death: date
    content: str
    author: str
    slug: str


desc = """
Empowering Memories Online

Welcome to Empowering Memories Online, where we honor and celebrate lives through heartfelt obituaries.
Our platform provides a dignified space to share cherished memories, commemorate milestones, and express condolences.
With thoughtful submissions managed seamlessly, we ensure each tribute is preserved with care and accessibility.
Discover a compassionate community dedicated to preserving legacies and offering solace during moments of loss.
Join us in celebrating lives lived and memories cherished on Empowering Memories Online.
    """


@app.route("/")
def home():

    img = url_for("static", filename="favicon.svg", _external=True)

    return render_template(
        "home.html",
        title="Home",
        canonical_url=url_for("home", _external=True),
        description=desc,
        og_image=img,
    )


@app.route("/form", methods=["POST", "GET", "DIALOG"])
def form():
    form = Posting(request.form)
    img = url_for("static", filename="favicon.svg", _external=True)

    if request.method == "POST":
        if form.validate():
            form_data = FormData(
                name=request.form["name"],
                date_of_birth=request.form["dob"],
                date_of_death=request.form["dod"],
                content=request.form["content"],
                author=request.form["author"],
                slug=request.form["slug"],
            )

            is_saved = save_to_db(form_data)

            if is_saved is not None:
                return render_template(
                    "submit_msg.html",
                    title="Form not submitted because of an error",
                    header="An error occured when trying to submit your memory, we are sorry :(",
                    msg=is_saved,
                    error=True,
                    canonical_url=url_for("form", _external=True),
                    description=desc,
                    og_image=img,
                )

            return render_template(
                "submit_msg.html",
                title="Form Submitted successfully",
                header=f"{form_data.author}, {form_data.name} will now be honored because of you!",
                msg="""
Thank you for submitting the obituary. Your contribution helps honor the memory of your loved one and shares their story with others.
If you have any further updates or would like to make changes, please don't hesitate to contact us.
We appreciate your trust in us during this difficult time.
                """,
                canonical_url=url_for("form", _external=True),
                description=desc,
                og_image=img,
            )

        else:
            validation_errors = form.errors
            return render_template(
                "submit_msg.html",
                title="Form validation errors",
                msg="We are glad that you're honoring your beloved, but we can't add them to our list of memories because of:",
                errors=validation_errors,
                error=True,
                canonical_url=url_for("form", _external=True),
                description=desc,
                og_image=img,
            )

    return render_template(
        "obituary_form.html",
        title="Form",
        form=form,
        canonical_url=url_for("form", _external=True),
        description=desc,
        og_image=img,
    )


def save_to_db(res: FormData) -> str | None:
    # Set up process
    init_sql = ""
    with open("init.sql", "r") as isql:
        init_sql = isql.read()

    conn = sqlite3.connect("obituary_platform")
    try:
        cur = conn.cursor()
        cur.execute(init_sql)
        conn.commit()

        # Now save the data
        cur.execute(
            """
            INSERT INTO obituaries (name, date_of_birth, date_of_death, content, author, slug)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                res.name,
                res.date_of_birth,
                res.date_of_death,
                res.content,
                res.author,
                res.slug,
            ),
        )
        conn.commit()
    except sqlite3.Error as e:
        if e.__str__() == "UNIQUE constraint failed: obituaries.slug":
            return f"The slug that you have submitted is already in use, please change it to something else\n\n`{res.slug}`"
        if e.__str__().__contains__("no such table"):
            return "An error occured on our side, the tables in which we place the memories cannot be found :("
        return "Data was not saved!"
    finally:
        # Close the connection no matter what
        conn.close()


@app.route("/view")
def view():
    img = url_for("static", filename="favicon.svg", _external=True)
    conn = sqlite3.connect("obituary_platform")
    req_id = request.args.get("id")
    try:
        obituaries = []
        cur = conn.cursor()
        if req_id is None:
            cur.execute("SELECT id, name, author, slug FROM obituaries")
            obituaries = cur.fetchall()
            if not obituaries:
                return render_template(
                    "submit_msg.html",
                    title="No one has sent their memories, can you be the first?",
                    msg="""
Sometimes silence can be the best memory that we have.

We have no memories in our collection, submit some through our form.
                    """,
                    error=True,
                    canonical_url=url_for("home", _external=True),
                    description=desc,
                    og_image=img,
                )
        else:
            cur.execute("SELECT * FROM obituaries WHERE id=?", (req_id,))
            obituaries = cur.fetchall()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        if e.__str__().__contains__("no such table"):
            return render_template(
                "submit_msg.html",
                title="500: An Error occured",
                msg="""
An error occured on our side, the tables in which we place the memories cannot be found :(
We'll try to create another one just for you!
""",
                canonical_url=url_for("view", _external=True),
                error=True,
                description=desc,
                og_image=img,
            )
    finally:
        conn.close()

    if req_id is None:
        return render_template(
            "view_obituaries.html",
            title="View Obituaries",
            obituaries=obituaries,
            canonical_url=url_for("view", _external=True),
            description=desc,
            og_image=img,
        )
    else:
        try:
            ob = obituaries[0]
            content = ob[4]
            if ob and ob[4]:
                content = Markup(
                    markdown2.markdown(ob[4])
                )  # Trust the user to do the right thing!
            return render_template(
                "details.html",
                title=ob[1],
                obituary=ob,
                time=f"{ob[6]} UTC ({humanize.naturaltime(datetime.strptime(ob[6], "%Y-%m-%d %H:%M:%S"))})",
                live_age=humanize.naturaldate(
                    datetime.strptime(ob[3], "%Y-%m-%d")
                    - datetime.strptime(ob[2], "%Y-%m-%d")
                ).split(",")[0],
                description=ob[7],
                og_image=img,
                content=content,
                canonical_url=url_for("view", _external=True),
            )
        except IndexError:
            return page_not_found("Id is out of range!!")


class Posting(Form):
    name = StringField("name", [validators.Length(min=4, max=95)])  # Max 100
    dob = DateField("dob", [validators.DataRequired()])  # Date of birth
    dod = DateField("dod", [validators.DataRequired()])  # Date of death
    content = StringField("content", [validators.Length(min=10)])  # Let them cook
    author = StringField("author", [validators.Length(min=4, max=95)])  # Max 100
    slug = StringField("slug", [validators.Length(min=7, max=250)])  # Max 255


@app.errorhandler(404)
def page_not_found(error):
    img = url_for("static", filename="favicon.svg", _external=True)
    app.logger.debug(error)
    return (
        render_template(
            "404.html",
            title="404 - Page Not Found",
            canonical_url=url_for("home", _external=True),
            description=desc,
            og_image=img,
        ),
        404,
    )


if __name__ == "__main__":
    app.run(debug=True)
