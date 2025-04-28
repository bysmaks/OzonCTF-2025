#include <gtk/gtk.h>
#include <cairo.h>
#include <vector>
#include <cstring>
#include <algorithm>


using namespace std;

#define CANVAS_SIZE 200

vector<vector<int>> originalImage(CANVAS_SIZE, vector<int>(CANVAS_SIZE, 0));
vector<vector<int>> userImage(CANVAS_SIZE, vector<int>(CANVAS_SIZE, 0));


const char M[8][9] = {
    "##   ##",
    "### ###",
    "#######",
    "## # ##",
    "##   ##",
    "##   ##",
    "##   ##",
    "       "
};

const char O[8][9] = {
    " #### ",
    "##  ##",
    "##  ##",
    "##  ##",
    "##  ##",
    "##  ##",
    " #### ",
    "       "
};

const char L[8][9] = {
    "##     ",
    "##     ",
    "##     ",
    "##     ",
    "##     ",
    "##     ",
    "###### ",
    "       "
};

const char D[8][9] = {
    "#####  ",
    "##  ## ",
    "##  ## ",
    "##  ## ",
    "##  ## ",
    "##  ## ",
    "#####  ",
    "       "
};

const char E[8][9] = {
    "###### ",
    "##     ",
    "##     ",
    "#####  ",
    "##     ",
    "##     ",
    "###### ",
    "       "
};

const char C[8][9] = {
    " ##### ",
    "##   ##",
    "##     ",
    "##     ",
    "##     ",
    "##   ##",
    " ##### ",
    "       "
};

void draw_large_letter(int x, int y, const char letter[8][9], int width = 8, int height = 8) {
    for (int i = 0; i < height; ++i)
        for (int j = 0; j < width; ++j)
            if (letter[i][j] == '#')
                if (y + i < CANVAS_SIZE && x + j < CANVAS_SIZE)
                    originalImage[y + i][x + j] = 1;
}


void create_original_image() {
    for (int i = 0; i < CANVAS_SIZE; ++i) {
        fill(originalImage[i].begin(), originalImage[i].end(), 0);
    }

    draw_large_letter(10, 10, M);
    draw_large_letter(30, 10, O);
    draw_large_letter(50, 10, L);
    draw_large_letter(70, 10, O);
    draw_large_letter(90, 10, D);
    draw_large_letter(110, 10, E);
    draw_large_letter(130, 10, C);

    int keyHandleWidth = 10;  
    int keyHandleHeight = 6;  
    int keyX = (CANVAS_SIZE - keyHandleWidth) / 2;
    int keyY = 110;

    for (int row = 0; row < keyHandleHeight; ++row) {
        for (int col = 0; col < keyHandleWidth; ++col) {
            if (keyY + row < CANVAS_SIZE && keyX + col < CANVAS_SIZE) {
                bool topOrBottom = (row == 0 || row == keyHandleHeight - 1);
                bool leftOrRight = (col == 0 || col == keyHandleWidth - 1);
                if (topOrBottom || leftOrRight)
                    originalImage[keyY + row][keyX + col] = 1;
            }
        }
    }

    int stemStartX = keyX + keyHandleWidth;
    int stemY = keyY + keyHandleHeight / 2;
    int stemLength = 15;
    for (int i = 0; i < stemLength; ++i) {
        int px = stemStartX + i;
        if (px < CANVAS_SIZE && stemY < CANVAS_SIZE)
            originalImage[stemY][px] = 1;
    }

    int toothX1 = stemStartX + stemLength / 2;
    int toothHeight = 4;
    for (int i = 1; i <= toothHeight; ++i) {
        int py = stemY + i;
        if (py < CANVAS_SIZE && toothX1 < CANVAS_SIZE)
            originalImage[py][toothX1] = 1;
    }

    int toothX2 = stemStartX + stemLength - 1;
    for (int i = 1; i <= toothHeight; ++i) {
        int py = stemY + i;
        if (py < CANVAS_SIZE && toothX2 < CANVAS_SIZE)
            originalImage[py][toothX2] = 1;
    }
}


bool check_drawing() {
    for (int i = 0; i < CANVAS_SIZE; ++i)
        for (int j = 0; j < CANVAS_SIZE; ++j)
            if (originalImage[i][j] != userImage[i][j])
                return false;
    return true;
}

void reset_drawing() {
    for (int i = 0; i < CANVAS_SIZE; ++i)
        for (int j = 0; j < CANVAS_SIZE; ++j)
            userImage[i][j] = 0;
}


void show_message(GtkWidget *parent, const char *message) {
    GtkWidget *dialog = gtk_message_dialog_new(GTK_WINDOW(parent),
                                               GTK_DIALOG_MODAL,
                                               GTK_MESSAGE_INFO,
                                               GTK_BUTTONS_OK,
                                               "%s", message);
    gtk_dialog_run(GTK_DIALOG(dialog));
    gtk_widget_destroy(dialog);
}


gboolean on_draw_event(GtkWidget *widget, cairo_t *cr, gpointer data) {
    cairo_set_source_rgb(cr, 1, 1, 1);
    cairo_paint(cr);

    cairo_set_source_rgb(cr, 0, 0, 0);
    cairo_rectangle(cr, 0, 0, CANVAS_SIZE, CANVAS_SIZE);
    cairo_stroke(cr);

    cairo_set_source_rgb(cr, 0, 0, 0);
    for (int i = 0; i < CANVAS_SIZE; ++i)
        for (int j = 0; j < CANVAS_SIZE; ++j)
            if (userImage[i][j] == 1) {
                cairo_rectangle(cr, j, i, 1, 1);
                cairo_fill(cr);
            }
    return FALSE;
}

gboolean on_mouse_move(GtkWidget *widget, GdkEventMotion *event, gpointer data) {
    int x = static_cast<int>(event->x);
    int y = static_cast<int>(event->y);
    if (x >= 0 && x < CANVAS_SIZE && y >= 0 && y < CANVAS_SIZE) {
        userImage[y][x] = 1;;
        gtk_widget_queue_draw(widget);
    }
    return TRUE;
}

void on_reset_button_clicked(GtkButton *button, gpointer data) {
    reset_drawing();
    gtk_widget_queue_draw(GTK_WIDGET(data));
}

void on_check_button_clicked(GtkButton *button, gpointer parent) {
    if (check_drawing())
        show_message(GTK_WIDGET(parent), "✅ Рисунок совпадает с эталоном!");
    else
        show_message(GTK_WIDGET(parent), "❌ Рисунок НЕ совпадает!");
}


void create_gui() {
    GtkWidget *window, *vbox, *canvas_frame, *canvas;
    GtkWidget *check_button, *reset_button;

    gtk_init(NULL, NULL);

    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window), "Рисовалка 200x200");
    gtk_window_set_resizable(GTK_WINDOW(window), FALSE);
    gtk_window_set_default_size(GTK_WINDOW(window), 250, 300);
    g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_container_set_border_width(GTK_CONTAINER(vbox), 20);
    gtk_container_add(GTK_CONTAINER(window), vbox);

    canvas_frame = gtk_frame_new(NULL);
    gtk_frame_set_shadow_type(GTK_FRAME(canvas_frame), GTK_SHADOW_IN);
    gtk_widget_set_halign(canvas_frame, GTK_ALIGN_CENTER);
    gtk_box_pack_start(GTK_BOX(vbox), canvas_frame, FALSE, FALSE, 0);

    canvas = gtk_drawing_area_new();
    gtk_widget_set_size_request(canvas, CANVAS_SIZE, CANVAS_SIZE);
    gtk_widget_add_events(canvas, GDK_BUTTON_PRESS_MASK | GDK_POINTER_MOTION_MASK);
    g_signal_connect(canvas, "draw", G_CALLBACK(on_draw_event), NULL);
    g_signal_connect(canvas, "motion-notify-event", G_CALLBACK(on_mouse_move), NULL);
    gtk_container_add(GTK_CONTAINER(canvas_frame), canvas);

    check_button = gtk_button_new_with_label("Проверить");
    g_signal_connect(check_button, "clicked", G_CALLBACK(on_check_button_clicked), window);
    gtk_box_pack_start(GTK_BOX(vbox), check_button, FALSE, FALSE, 0);

    reset_button = gtk_button_new_with_label("Сбросить");
    g_signal_connect(reset_button, "clicked", G_CALLBACK(on_reset_button_clicked), canvas);
    gtk_box_pack_start(GTK_BOX(vbox), reset_button, FALSE, FALSE, 0);

    gtk_widget_show_all(window);
    gtk_main();
}


int main() {
    create_original_image();
    create_gui();


    return 0;
}
