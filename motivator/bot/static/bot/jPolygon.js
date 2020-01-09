function angle(cx, cy, ex, ey) {
  var dy = ey - cy;
  var dx = ex - cx;
  return Math.atan2(dy, dx);
}

class TextConfigurationSetup {
    constructor(canvas) {
        this.canvas = canvas;

        this.polygon = [];
        this.isClosed = false;
        this.stage = 'bounds';
        this.text = [];

        this.img = new Image();
        this.img.src = canvas.getAttribute('data-imgsrc');
        this.img.onload = () => {
            this.canvas.width = this.img.width;
            this.canvas.height = this.img.height;
            this.context = canvas.getContext('2d');
            this.draw();
        }
    }

    line_intersects = (p0, p1, p2, p3) => {
        let s1_x, s1_y, s2_x, s2_y;
        s1_x = p1[0] - p0[0];
        s1_y = p1[1] - p0[1];
        s2_x = p3[0] - p2[0];
        s2_y = p3[1] - p2[1];

        const s = (-s1_y * (p0[0] - p2[0]) + s1_x * (p0[1] - p2[1])) / (-s2_x * s1_y + s1_x * s2_y);
        const t = (s2_x * (p0[1] - p2[1]) - s2_y * (p0[0] - p2[0])) / (-s2_x * s1_y + s1_x * s2_y);

        return s >= 0 && s <= 1 && t >= 0 && t <= 1;
    };

    check_intersect = (x, y) => {
        if (this.polygon.length < 4) {
            return false;
        }
        const p0 = [], p1 = [], p2 = [], p3 = [];
        p2[0] = this.polygon[this.polygon.length - 1][0];
        p2[1] = this.polygon[this.polygon.length - 1][1];
        p3[0] = x;
        p3[1] = y;

        for (let i = 0; i < this.polygon.length - 1; i++) {
            p0[0] = this.polygon[i][0];
            p0[1] = this.polygon[i][1];
            p1[0] = this.polygon[i + 1][0];
            p1[1] = this.polygon[i + 1][1];
            if (p1[0] === p2[0] && p1[1] === p2[1]) {
                continue;
            }
            if (p0[0] === p3[0] && p0[1] === p3[1]) {
                continue;
            }
            if (this.line_intersects(p0, p1, p2, p3) === true) {
                return true;
            }
        }
        return false;
    };

    canvasClick = (event) => {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        if (this.stage === 'bounds' && !this.isClosed) {
            if (!this.check_intersect(x, y)) {
                this.polygon.push([~~x, ~~y])
            }
        } else if (this.stage === 'text_start') {
            this.stage = 'text_angle';
            this.origin = [~~x, ~~y];
        } else if (this.stage === 'text_angle') {
            this.angle = angle(this.origin[0], this.origin[1], ~~x, ~~y);
            this.cursor = [~~x,~~y];
            this.stage = 'text_content';
        }
        this.draw()
    };

    canvasMouseMove = (event) => {
        if (this.stage === 'text_angle') {
            const rect = this.canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            this.cursor = [~~x, ~~y];
            this.draw()
        }
    };

    canvasKey = (event) => {
        if (event.key === 'Enter' && this.stage === 'bounds' && this.polygon.length > 2) {
            this.isClosed = true;
            this.stage = 'text_start';
            this.draw();
        } else if (this.stage === 'text_content'){
            console.log(event.key);
            if (event.keyCode === 8){
                this.text.pop();
            }
            else if (event.key === 'Enter'){
                this.text.push('\n');
            }
            else {
                this.text.push(String.fromCharCode(event.keyCode))
            }
            this.draw();
        }
    };

    draw = () => {
        this.context.drawImage(this.img, 0, 0);
        // Draw vertices
        this.context.fillStyle = "white";
        this.context.strokeStyle = "3px white";
        this.polygon.forEach((point) => {
            this.context.fillRect(point[0] - 2, point[1] - 2, 4, 4);
        });

        // Draw edges
        if (this.polygon.length > 1) {
            this.context.beginPath();

            let previous_point = this.polygon[0];
            this.context.moveTo(previous_point[0], previous_point[1]);
            for (let i = 1; i < this.polygon.length; i++) {
                const current_point = this.polygon[i];
                this.context.lineTo(current_point[0], current_point[1]);
                this.context.moveTo(current_point[0], current_point[1]);
            }
            if (this.polygon.length >= 3 && this.isClosed) {
                this.context.lineTo(this.polygon[0][0], this.polygon[0][1]);
            }
            this.context.closePath();
        }
        this.context.stroke();

        if (this.origin) {
            this.context.fillRect(this.origin[0] - 3, this.origin[1] - 3, 6, 6);
        }
        if (this.stage === 'text_angle' && this.cursor){
            this.context.moveTo(this.origin[0], this.origin[1]);
            this.context.lineTo(this.cursor[0], this.cursor[1]);
            this.context.stroke();
        }
        if (this.stage === 'text_content'){
            this.context.save();
            this.context.translate(this.origin[0], this.origin[1]);
            this.context.rotate(this.angle);
            this.context.font = '24px Arial';
            this.context.fillText(this.text.join(''), 0, 0);
            this.context.restore();
        }
    }
}